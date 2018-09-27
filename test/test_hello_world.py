from f9k9.app import app

with app.test_client() as c:
    rv = c.get('/')
    assert rv.status_code is 200


