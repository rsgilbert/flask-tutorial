import pytest
from flask import g, session
from flaskr.db import get_db


def test_register_get(client, app):
    assert client.get('/auth/register').status_code == 200


def test_register_post(client, app):
    response = client.post('/auth/register', data={'username': 'Kenny', 'password': 'k100'})
    assert response.headers['location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute("SELECT * FROM user WHERE username = 'Kenny'").fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), [
    ('', '', 'Username is required'),
    ('a', '', 'Password is required'),
    ('rob', 'rob', 'already registered')
])
def test_register_validate_input(client, username, password, message):
    response = client.post('/auth/register', data={'username': username, 'password': password})
    data = response.get_data(as_text=True)
    assert message in data


def test_login_status_code(client):
    assert client.get('/auth/login').status_code == 200


def test_login(auth, client):
    response = auth.login()
    assert response.headers['location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'rob'


@pytest.mark.parametrize(('username', 'password', 'message'), [
    ('babe', 'abc', 'No user found with given username'),
    ['rob', 'abc', 'Incorrect password']
])
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    data = response.get_data(as_text=True)
    assert message in data


def test_logout(client):
    with client:
        client.get('/auth/logout')
        assert 'user_id' not in session
