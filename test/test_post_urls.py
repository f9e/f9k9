from f9k9.app import app
from werkzeug.datastructures import MultiDict

app.config['APP_PROXY'] = True
with app.test_client() as c:
    endpoint_url = "http://localhost:5000/api/v1.0.0/identify/"
    data = MultiDict()
    data.add('urls', ['https://ipfs.io/ipfs/QImAnInvalidHashhhhhhhh/cat.jpg',
                      'https://ipfs.io/ipfs/QmW2WQi7j6c7UgJTarActp7tDNikE4B2qXtFCfLPdsgaTQ/cat.jpg',
                      'https://upload.wikimedia.org/wikipedia/commons/b/b9/CyprusShorthair.jpg',
                      'https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg']
             )
    rv = c.post(endpoint_url,
                data=data,
                content_type='application/json')
    # TODO this post returns no content... for some reason
    # assert rv.status_code == 207
