import pytest
from urllib.parse import urlsplit, urlencode
from flask import url_for
from flask_login import current_user
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


@pytest.mark.vcr()
def test_github_oauth_logout(app, session, client):
    assert current_user.is_authenticated is False

    client.get(url_for('oauth.github_oauth_callback'), query_string={'code': 'c3cccd15fe3dbbaa5d7d'})

    assert current_user.is_authenticated is True

    client.get(url_for('oauth.logout'))

    assert current_user.is_authenticated is False


@pytest.mark.vcr()
@pytest.mark.parametrize('request_order', [('gh', 'bb', 'gl'), ('gh', 'gl', 'bb'),
                                           ('gl', 'gh', 'bb'), ('gl', 'bb', 'gh'),
                                           ('bb', 'gh', 'gl'),  ('bb', 'gl', 'gh')])
def test_github_merge_accounts(app, session, client, request_order):
    accounts = Account.query.all()
    assert len(accounts) == 0

    def do_request(r):
        if r == 'gh':
            client.get(url_for('oauth.github_oauth_callback'), query_string={'code': 'c3cccd15fe3dbbaa5d7d'})
        elif r == 'bb':
            client.get(url_for('oauth.bitbucket_oauth_callback'), query_string={'code': 'JKkyDwK6xpTqK7Pf8x'})
        else:
            client.get(url_for('oauth.gitlab_oauth_callback'), query_string={'code': '6be7d9f95c2edb413fdf0c5a88bbe071460ce62a6df6a77a17177e98c7146456'})

    for req in request_order:
        do_request(req)

    account = Account.query.filter(Account.id == 1).first()
    assert account.github_id == 18519037
    assert account.github_login == 'SethMichaelLarson'
    assert account.github_access_token is not None

    assert account.bitbucket_id == '557058:124692a0-29e0-4784-92ee-87f534c17ec0'
    assert account.bitbucket_login == 'armonaut'
    assert account.bitbucket_access_token is not None
    assert account.bitbucket_refresh_token is not None

    assert account.gitlab_id == 1195202
    assert account.gitlab_login == 'SethMichaelLarson'
    assert account.gitlab_access_token is not None
    assert account.gitlab_refresh_token is not None
