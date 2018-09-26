from flask import Flask, request, render_template, jsonify, Response
from flask_restplus import Api, Resource, fields
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from tensorflow import get_default_graph
from PIL import Image
from hashlib import md5 as hashfunc
import os, json
import requests as external
from tempfile import SpooledTemporaryFile

CLASSIFIER_MODEL = os.environ.get("CLASSIFIER_MODEL",
                                  default='./storage/ecdf7924eb6ba16cf1a8cdd4307e7d2f.hdf5')
CLASSIFIER_TRUE = os.environ.get("CLASSIFIER_TRUE", default='Dog')
CLASSIFIER_FALSE = os.environ.get("CLASSIFIER_FALSE", default='Cat')
CLASSIFIER_THRESH = os.environ.get("CLASSIFIER_THRESH", default=0.5)

# TODO default to false
# Controls whether API will get images from the internet on the fly

ALLOW_PROXY = os.environ.get("ALLOW_PROXY", default=True)

global model, graph

# load the pre-trained Keras model
model = load_model(CLASSIFIER_MODEL)
graph = get_default_graph()

app = Flask(__name__)

api = Api(app,
          version='1.0.1',
          title='f9k9 - Feline Canine',
          description='Rest API for a general purpose binary image classifier',
          )

ns = api.namespace('identify', description='Endpoint to identify images')

ALLOWED_EXTENSIONS = set(['bmp', 'gif', 'ico', 'jpg', 'jpeg', 'psd', 'png', 'tif'])


def init():
    global model, graph

    # load the pre-trained Keras model
    model = load_model(CLASSIFIER_MODEL)
    graph = get_default_graph()


def human_text_func(p):
    return CLASSIFIER_TRUE if p > CLASSIFIER_THRESH else CLASSIFIER_FALSE


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def prepare_data_array(file, height=150, width=150, num_channels=3):
    image = Image.open(file)
    if num_channels == 3 and image.mode != "RGB":
        image = image.convert('RGB')
    image = image.resize((width, height))
    img_arr = img_to_array(image)
    img_arr = img_arr.reshape((1,) + img_arr.shape)
    img_arr = 1 / 255.0 * img_arr
    return img_arr


def get_verbosity(request):
    if request.args.get('verbose') == 'true':
        return True
    elif 'verbose' in request.form and request.form['verbose'] == 'true':
        return True
    else:
        return False


def build_response_object(p, file, verbose, is_error=False):

    if is_error:
        value, result = p, 'Error'
        if verbose:
            result += ' ' + p
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
    responses = []

    # Make sure downloading via proxy is enabled.
    if ALLOW_PROXY:
        images = []
        for url in urls:
            r = external.get(url)
            if r.status_code == 200:
                with SpooledTemporaryFile(max_size=250e3) as tmp:
                    print('here')
                    tmp.write(r.content)
                    tmp.filename = url
                    responses += handle_files(files=[tmp],
                                              verbose=verbose)

            else:
                file = SpooledTemporaryFile(max_size=10)
                file.filename = url
                responses += build_response_object(p="- Downloading : {}".format(r.status_code),
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
    return responses


def get_status_code(responses, verbose):

    has_errors, has_success = False, False
    if verbose:
        if any(x['is_error'] for x in responses):
            has_errors = True
        if any(not x['is_error'] for x in responses):
            has_success = True
    else:
        if "Error" in responses:
            has_errors = True
        if CLASSIFIER_TRUE in responses or CLASSIFIER_FALSE in responses:
            has_success = True

    if has_success:
        if has_errors:
            return 207  # Mixed
        else:
            return 200  # Success
    else:
        if has_errors:
            return 400  # Error
        else:
            return 204  # No Content


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route("/api/v1.0.0/identify/", methods=["GET", "POST", "PUT"])
def run_list():
    # get if verbosity was true from either data or params
    verbose = get_verbosity(request)

    responses = []

    if 'Content-Type' in request.headers.keys():
        if 'multipart/form-data' in request.headers['Content-Type']:
            files = request.files.getlist("images")
            responses += handle_files(files, verbose)

    # Download image urls or url and process them
    urls = []
    if 'url' in request.form.keys():
        urls += request.form.getlist('url')
    if 'urls[]' in request.form.keys():
        urls += request.form.getlist('urls[]')

    if urls:
        responses += handle_urls(urls, verbose)

    # No content type, hail-mary assume image file was put
    if 'Content-Type' not in request.headers.keys():
        with SpooledTemporaryFile(max_size=250e3) as tmp:
            tmp.write(request.get_data())
            responses += handle_files([tmp], verbose)

    status_code = get_status_code(responses, verbose)

    return Response(json.dumps(responses), status=status_code, mimetype='application/json')


@app.route("/api/v1.0.0/identify/<filename>", methods=["PUT"])
def run_singleton(filename):
    verbose = True if 'verbose' in request.form else False
    responses = []

    with SpooledTemporaryFile(max_size=250e3) as tmp:
        tmp.write(request.get_data())
        if filename:
            tmp.filename = filename
        responses += handle_files([tmp], verbose)

    status_code = get_status_code(responses, verbose)

    return Response(json.dumps(responses), status=status_code, mimetype='application/json')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
