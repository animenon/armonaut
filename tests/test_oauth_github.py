import pytest
from urllib.parse import urlsplit, urlencode
from flask import url_for
from armonaut.models import Account


def test_github_oauth_handshake(app, client):
    r = client.get(url_for('oauth.github_oauth_handshake'))
    assert r.status_code == 302

    url = urlsplit(r.location)
    assert url.scheme == 'https'
    assert url.netloc == 'github.com'
    assert url.path == '/login/oauth/authorize'
    assert f'client_id={app.config.get("GITHUB_OAUTH_ID")}' in url.query
    assert 'response_type=code' in url.query
    assert urlencode({'redirect_uri': url_for('oauth.github_oauth_callback', _external=True)}) in url.query


@pytest.mark.vcr()
def test_github_oauth_callback(app, session, client):
    accounts = Account.query.all()
    assert len(accounts) == 0

    r = client.get(url_for('oauth.github_oauth_callback'), query_string={'code': 'c3cccd15fe3dbbaa5d7d'})
    assert r.status_code == 302
    assert r.location == url_for('index.home', _external=True)

    account = Account.query.filter(Account.id == 1).first()
    assert account.github_id == 18519037
    assert account.github_login == 'SethMichaelLarson'
    assert account.github_access_token is not None
