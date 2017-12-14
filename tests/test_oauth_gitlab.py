import pytest
from urllib.parse import urlsplit, urlencode
from flask import url_for
from flask_login import current_user
from armonaut.models import Account


def test_gitlab_oauth_handshake(app, client):
    r = client.get(url_for('oauth.gitlab_oauth_handshake'))
    assert r.status_code == 302

    url = urlsplit(r.location)
    assert url.scheme == 'https'
    assert url.netloc == 'gitlab.com'
    assert url.path == '/oauth/authorize'
    assert f'client_id={app.config.get("GITLAB_OAUTH_ID")}' in url.query
    assert 'response_type=code' in url.query
    assert urlencode({'redirect_uri': url_for('oauth.gitlab_oauth_callback', _external=True)}) in url.query


@pytest.mark.vcr()
def test_gitlab_oauth_callback(app, session, client):
    accounts = Account.query.all()
    assert len(accounts) == 0

    r = client.get(url_for('oauth.gitlab_oauth_callback'), query_string={'code': '6be7d9f95c2edb413fdf0c5a88bbe071460ce62a6df6a77a17177e98c7146456'})
    assert r.status_code == 302
    assert r.location == url_for('index.home', _external=True)

    account = Account.query.filter(Account.id == 1).first()
    assert account.gitlab_id == 1195202
    assert account.gitlab_login == 'SethMichaelLarson'
    assert account.gitlab_access_token is not None
    assert account.gitlab_refresh_token is not None


@pytest.mark.vcr()
def test_gitlab_oauth_logout(app, session, client):
    assert current_user.is_authenticated is False

    client.get(url_for('oauth.gitlab_oauth_callback'), query_string={'code': '6be7d9f95c2edb413fdf0c5a88bbe071460ce62a6df6a77a17177e98c7146456'})

    assert current_user.is_authenticated is True

    client.get(url_for('oauth.logout'))

    assert current_user.is_authenticated is False
