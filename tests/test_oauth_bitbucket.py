import pytest
from urllib.parse import urlsplit, urlencode
from flask import url_for
from flask_login import current_user
from armonaut.models import Account


def test_bitbucket_oauth_handshake(app, client):
    r = client.get(url_for('oauth.bitbucket_oauth_handshake'))
    assert r.status_code == 302

    url = urlsplit(r.location)
    assert url.scheme == 'https'
    assert url.netloc == 'bitbucket.org'
    assert url.path == '/site/oauth2/authorize'
    assert f'client_id={app.config.get("BITBUCKET_OAUTH_ID")}' in url.query
    assert 'response_type=code' in url.query


@pytest.mark.vcr()
def test_bitbucket_oauth_callback(app, session, client):
    accounts = Account.query.all()
    assert len(accounts) == 0

    r = client.get(url_for('oauth.bitbucket_oauth_callback'), query_string={'code': 'JKkyDwK6xpTqK7Pf8x'})
    assert r.status_code == 302
    assert r.location == url_for('index.home', _external=True)

    account = Account.query.filter(Account.id == 1).first()
    assert account.bitbucket_id == '557058:124692a0-29e0-4784-92ee-87f534c17ec0'
    assert account.bitbucket_login == 'armonaut'
    assert account.bitbucket_access_token is not None
    assert account.bitbucket_refresh_token is not None


@pytest.mark.vcr()
def test_bitbucket_oauth_logout(app, session, client):
    assert current_user.is_authenticated is False

    client.get(url_for('oauth.bitbucket_oauth_callback'), query_string={'code': 'JKkyDwK6xpTqK7Pf8x'})

    assert current_user.is_authenticated is True

    client.get(url_for('oauth.logout'))

    assert current_user.is_authenticated is False
