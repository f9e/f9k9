from flask import Flask, request, render_template, jsonify
from flask_restplus import Api, Resource, fields
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from tensorflow import get_default_graph
from PIL import Image
from hashlib import md5 as hashfunc

app = Flask(__name__)

api = Api(app,
          version='1.0.1',
          title='Little Cat Dog',
          description='Rest API for binary image classifier',
          )

ns = api.namespace('identify', description='Endpoint to identify images')


ALLOWED_EXTENSIONS = set(['bmp',
                          'gif',
                          'ico',
                          'jpg', 'jpeg',
                          'psd', 'png',
                          'tif'])


def human_text_func(p):
    return 'Dog' if p > 0.5 else 'Cat'


def init():
    global model, graph
    # load the pre-trained Keras model
    model = load_model('./storage/ecdf7924eb6ba16cf1a8cdd4307e7d2f.hdf5')
    graph = get_default_graph()


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


@app.route('/')
def welcome():
    return render_template('index.html')


def build_response(p, file, verbose):
    p_str = human_text_func(p)
    if verbose:
        filehash = hashfunc(file.read()).hexdigest()
        return [
            {'hash': filehash,
             'hash_func': hashfunc.name,
             'filename': file.filename,
             'value': p,
             'result': p_str
             }
        ]
    else:
        return [p_str]


def build_response_error(err, file, verbose):

    if verbose:
        file_hash = hashfunc(file.read()).hexdigest()
        return [
            {'hash': file_hash,
             'hash_func': hashfunc.name,
             'filename': file.filename,
             'value': None,
             'result': 'Error %s' % err
             }
        ]
    else:
        return ["Error"]


def handle_multipart_form(request, verbose):
    responses = []

    for file in request.files.getlist("images"):
        with graph.as_default():
            try:
                if not allowed_file(file.filename):
                    raise NotImplementedError

                # Get the input dimensions from the model
                w, h, c = (d.value for d in model.inputs[0].shape[1:])

                x = prepare_data_array(file=file,
                                       width=w,
                                       height=h,
                                       num_channels=c,
                                       )

                predictions = model.predict(x=x, verbose=0)
                p = float(predictions[0][0])

                responses += build_response(p=p,
                                            file=file,
                                            verbose=verbose)

            except NotImplementedError as err:
                responses += build_response_error(err=err,
                                                  file=file,
                                                  verbose=verbose)

    return responses


@app.route("/api/v1.0.0/identify/", methods=["GET", "POST"])
def run():
    verbose = True if 'verbose' in request.form else False
    responses = []

    if 'multipart/form-data' in request.headers['Content-Type']:
        responses += handle_multipart_form(request, verbose)

    elif request.headers['Content-Type'] == 'text/plain':
        return jsonify(responses)

    elif request.headers['Content-Type'] == 'application/json':
        return jsonify(responses)

    return jsonify(responses)


if __name__ == '__main__':
    init()
    app.run(host='0.0.0.0')
