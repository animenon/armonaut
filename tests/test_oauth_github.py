import pytest
from urllib.parse import urlsplit, urlencode
from flask import url_for


@pytest.mark.vcr()
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
