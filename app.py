from flask import Flask, request, render_template, jsonify, Response
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from tensorflow import get_default_graph
from PIL import Image
from hashlib import md5 as hashfunc
import os, json
import requests as external
from tempfile import SpooledTemporaryFile

APP_MODEL = os.environ.get("APP_MODEL",
                           default='./storage/ecdf7924eb6ba16cf1a8cdd4307e7d2f.hdf5')
APP_TRUE = os.environ.get("APP_TRUE", default='Dog')
APP_FALSE = os.environ.get("APP_FALSE", default='Cat')
APP_THRESH = os.environ.get("APP_THRESH", default=0.5)

# TODO default to false
# Controls whether API will get images from the internet on the fly

APP_PROXY = os.environ.get("APP_PROXY", default=True)

global model, graph

# load the pre-trained Keras model
model = load_model(APP_MODEL)
graph = get_default_graph()

app = Flask(__name__)

# api = Api(app,
#          version='1.0.1',
#          title='f9k9 - Feline Canine',
#          description='Rest API for a general purpose binary image classifier',
#          )

# ns = api.namespace('identify', description='Endpoint to identify images')

ALLOWED_EXTENSIONS = set(['bmp', 'gif', 'ico',
                          'jpg', 'jpeg',
                          'png', 'tif'])


def init():
    global model, graph

    # load the pre-trained Keras model
    model = load_model(APP_MODEL)
    graph = get_default_graph()


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route("/api/v1.0.0/identify/", methods=["GET", "POST", "PUT"])
def run_list():
    responses = []

    # get if verbosity was true from either data or params
    verbose = get_verbosity(request)

    if 'Content-Type' in request.headers.keys():
        if 'multipart/form-data' in request.headers['Content-Type']:
            files = request.files.getlist("images")
            responses += handle_files(files, verbose)

    # Download image urls or url and process them
    urls = get_urls(request)
    print(urls)
    if urls:
        responses += handle_urls(urls, verbose)

    # No content type, hail-mary assume image file was put
    if 'Content-Type' not in request.headers.keys():
        with SpooledTemporaryFile(max_size=250e3) as tmp:
            tmp.write(request.get_data())
            responses += handle_files([tmp], verbose)

    status_code = get_status_code(responses, verbose)

    return Response(json.dumps(responses),
                    status=status_code,
                    mimetype='application/json')


@app.route("/api/v1.0.0/identify/<filename>", methods=["PUT", "POST"])
def run_singleton(filename):
    verbose = get_verbosity(request)
    responses = []

    with SpooledTemporaryFile(max_size=250e3) as tmp:
        tmp.write(request.get_data())
        if filename:
            tmp.filename = filename
        responses += handle_files([tmp], verbose)

    status_code = get_status_code(responses, verbose)

    return Response(json.dumps(responses),
                    status=status_code,
                    mimetype='application/json')


def prepare_data_array(file, height=150, width=150, num_channels=3):
    """Marshal a file to a normalized 3d-array"""
    image = Image.open(file)
    if num_channels == 3 and image.mode != "RGB":
        image = image.convert('RGB')
    image = image.resize((width, height))
    img_arr = img_to_array(image)
    img_arr = img_arr.reshape((1,) + img_arr.shape)
    img_arr = 1 / 255.0 * img_arr
    return img_arr


def build_response_object(p, file, verbose, is_error=False):
    """Build a response object"""
    if is_error:
        value, result = None, 'Error'
        if verbose:
            print(p)
            # TODO return better error message
            result += ' '.format(p)
    else:
        value, result = p, human_text_func(p)

    if not verbose:
        return [result]
    else:
        try:
            file_hash = hashfunc(file.read()).hexdigest()
        except:
            file_hash = ""

        try:
            filename = file.filename
        except AttributeError:
            filename = ''

        return [
            {'hash': file_hash,
             'hash_func': hashfunc.__name__,
             'filename': filename,
             'value': value,
             'result': result,
             'is_error': 'Error' in result
             }
        ]


def handle_urls(urls, verbose):
    """Returns the model evaluation for a list of urls"""
    responses = []

    # Make sure downloading via proxy is enabled.

    if APP_PROXY:
        images = []
        for url in urls:
            r = external.get(url)
            if r.status_code == 200:
                with SpooledTemporaryFile(max_size=250e3) as tmp:
                    tmp.write(r.content)
                    tmp.filename = url
                    responses += handle_files(files=[tmp],
                                              verbose=verbose)

            else:
                file = SpooledTemporaryFile(max_size=10)
                file.filename = url
                message = " - Downloading : {}".format(r.status_code)
                responses += build_response_object(p=message,
                                                   file=file,
                                                   verbose=verbose,
                                                   is_error=True)

    else:
        for url in urls:
            file = SpooledTemporaryFile(max_size=10)
            file.filename = url
            responses += build_response_object(p="Proxy Download Disabled",
                                               file=file,
                                               verbose=verbose,
                                               is_error=True)
    return responses


def handle_files(files, verbose):
    """Returns the model evaluation for a list of files"""
    responses = []

    for file in files:
        with graph.as_default():
            try:
                # Get the input dimensions from the model
                w, h, c = (d.value for d in model.inputs[0].shape[1:])

                x = prepare_data_array(file=file,
                                       width=w,
                                       height=h,
                                       num_channels=c,
                                       )

                # Get the value of the prediction
                predictions = model.predict(x=x, verbose=0)
                p = float(predictions[0][0])

                responses += build_response_object(p=p,
                                                   file=file,
                                                   verbose=verbose)

            except NotImplementedError as err:
                responses += build_response_object(p=err,
                                                   file=file,
                                                   verbose=verbose,
                                                   is_error=True)
            except OSError as err:
                responses += build_response_object(p=err,
                                                   file=file,
                                                   verbose=verbose,
                                                   is_error=True)
    return responses


def get_errors_and_successes(responses, verbose):
    """Convenience function to determine state"""
    has_errors, has_success = False, False

    if verbose:
        if any(x['is_error'] for x in responses):
            has_errors = True
        if any(not x['is_error'] for x in responses):
            has_success = True
    else:
        if "Error" in responses:
            has_errors = True
        if APP_TRUE in responses or APP_FALSE in responses:
            has_success = True

    return has_errors, has_success


def get_status_code(responses, verbose):
    """Convenience function to return status codes"""
    has_errors, has_success = get_errors_and_successes(responses, verbose)

    code_map = {
        True: {  # has success
            True: 207,  # with failures
            False: 200  # sans failures
        },
        False: {  # No Successes
            True: 400,  # with failures
            False: 204  # sans failures
        }
    }

    return code_map[has_success][has_errors]


def human_text_func(p):
    """Evalue the app boolean to a human readable value"""
    return APP_TRUE if p > APP_THRESH else APP_FALSE


def allowed_file(filename):
    """Check if filename is supported"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_urls(request):
    """Build list of urls, if pass in form or as parameter"""
    urls = []

    if request.args.get('url'):
        urls += [request.args.getlist('url')]
    if request.args.get('urls'):
        urls += [request.args.getlist('urls')]
    if 'url' in request.form.keys():
        urls += request.form.getlist('url')
    if 'urls' in request.form.keys():
        urls += request.form.getlist('urls')
    return urls


def get_verbosity(request):
    """Get verbose param, if pass in form or as parameter"""
    if request.args.get('verbose'):
        return request.args.get('verbose').lower() == 'true'
    elif 'verbose' in request.form:
        return request.form['verbose'].lower() == 'true'
    else:
        return False


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
