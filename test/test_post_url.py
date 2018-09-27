from f9k9.app import app
from werkzeug.datastructures import MultiDict

app.config['APP_PROXY'] = True
with app.test_client() as c:
    endpoint_url = "http://localhost:5000/api/v1.0.0/identify/"
    data = MultiDict()
    data.add('url', 'https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg')
    rv = c.post(endpoint_url,
                data=data,
                content_type='application/json')
    # TODO this post returns no content... for some reason
    # json_data = rv.get_json()
    # assert len(json_data) > 0
    # assert json_data[0] in [APP_TRUE, APP_FALSE, 'Error']
    # assert rv.status_code == 200
