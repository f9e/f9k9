from f9k9.app import app
from werkzeug.datastructures import FileMultiDict
from glob import glob
import os

APP_TRUE = os.environ.get("APP_TRUE", default='Dog')
APP_FALSE = os.environ.get("APP_FALSE", default='Cat')


with app.test_client() as c:
    endpoint_url = "http://localhost:5000/api/v1.0.0/identify/"
    filenames = glob('./static/*')
    files = FileMultiDict()
    for filename in filenames:
        files.add_file('images',
                       file=open(filename, 'r+b'),
                       filename=filename)
    rv = c.post(endpoint_url,
                data=files,
                content_type='multipart/form-data')
    json_data = rv.get_json()
    assert len(json_data) > 0
    assert json_data[0] in [APP_TRUE, APP_FALSE, 'Error']
    assert rv.status_code == 207
    for f in files.getlist('images'):
        f.close()
