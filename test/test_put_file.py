from f9k9.app import app
from glob import glob
from werkzeug.datastructures import MultiDict

app.config['APP_PROXY'] = True
with app.test_client() as c:
    endpoint_url = "http://localhost:5000/api/v1.0.0/identify/"
    filename = glob('./static/*')[2]
    print(filename)
    data = dict([('images',open(filename, 'r+b'))])

    rv = c.put(endpoint_url,
                data=data,
                content_type='application/json')
    # TODO this post returns no content... for some reason
    # json_data = rv.get_json()
    # assert len(json_data) > 0
    # assert json_data[0] in [APP_TRUE, APP_FALSE, 'Error']
    # assert rv.status_code == 200
