# Copyright (C) 2017 Seth Michael Larson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from urllib.parse import urlparse, urljoin, urlencode
import requests
from flask import Blueprint, url_for, redirect, current_app, request, flash
from flask_login import current_user, login_user, logout_user
from armonaut import db
from armonaut.models import Account


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/github/handshake', methods=['GET'])
def github_oauth_handshake():
    if not current_user.is_anonymous and current_user.github_id is not None:
        return redirect(url_for('index.home'))
    query = urlencode({'client_id': current_app.config.get("GITHUB_OAUTH_ID"),
                       'response_type': 'code',
                       'redirect_uri': url_for('oauth.github_oauth_callback', _external=True),
                       'scope': 'user:email read:org repo'})
    return redirect(f'https://github.com/login/oauth/authorize?{query}')


@oauth.route('/github/callback', methods=['GET'])
def github_oauth_callback():
    # Exchange our OAuth code for an access token.
    with requests.post('https://github.com/login/oauth/access_token',
                       headers={'Accept': 'application/json'},
                       params={'client_id': current_app.config.get('GITHUB_OAUTH_ID'),
                               'client_secret': current_app.config.get('GITHUB_OAUTH_SECRET'),
                               'redirect_uri': url_for('oauth.github_oauth_callback', _external=True),
                               'code': request.args.get('code')}) as r:
        if not r.ok:
            flash('Couldn\'t authenticate with GitHub', 'error')
            return redirect(url_for('index.home'))
        access_token = r.json()['access_token']

    # Check the validity of the access token by trying to use it.
    with requests.get('https://api.github.com/user',
                      headers={'Accept': 'application/json',
                               'Authorization': f'token {access_token}'}) as r:
        if not r.ok:
            flash('Couldn\'t authenticate with GitHub', 'error')
            return redirect(url_for('index.home'))
        github_id = r.json()['id']
        github_login = r.json()['login']
        github_email = r.json()['email']

        if not current_user.is_anonymous and \
                current_user.github_id is not None and \
                current_user.github_id != github_id:
            logout_user()
        if current_user.is_anonymous:
            user = Account.query.filter(Account.github_id == github_id).first()
            if user is None:
                user = Account()
        else:
            user = current_user

        user.github_id = github_id
        user.github_login = github_login
        user.github_email = github_email
        user.github_access_token = access_token

        db.session.add(user)
        db.session.commit()
        login_user(user)

    return redirect(url_for('index.home'))


@oauth.route('/bitbucket/handshake', methods=['GET'])
def bitbucket_oauth_handshake():
    if not current_user.is_anonymous and current_user.bitbucket_id is not None:
        return redirect(url_for('index.home'))
    redirect_uri = url_for('oauth.bitbucket_oauth_callback', _external=True)
    return redirect(f'https://bitbucket.org?'
                    f'client_id={current_app.config.get("BITBUCKET_OAUTH_ID")}&'
                    f'response_type=code&'
                    f'redirect_uri={redirect_uri}&'
                    f'state=state')


@oauth.route('/bitbucket/callback', methods=['GET'])
def bitbucket_oauth_callback():
    pass


@oauth.route('/gitlab/handshake', methods=['GET'])
def gitlab_oauth_handshake():
    if not current_user.is_anonymous and current_user.gitlab_id is not None:
        return redirect(url_for('index.home'))
    redirect_uri = url_for('oauth.gitlab_oauth_callback')
    return redirect(f'https://gitlab.com/oauth/authorize?'
                    f'response_type=code&'
                    f'redirect_uri={redirect_uri}&'
                    f'state=state')


@oauth.route('/gitlab/callback', methods=['GET'])
def gitlab_oauth_callback():
    pass


def is_safe_url(url) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)
