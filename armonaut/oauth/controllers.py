from flask import Blueprint, url_for, redirect, current_app
from flask_login import current_user


oauth = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth.route('/github_oauth_handshake', methods=['GET'])
def github_oauth_handshake():
    if not current_user.is_anonymous and current_user.github_id is not None:
        return redirect(url_for('index.home'))
    redirect_uri = url_for('oauth.github_oauth_callback', _external=True)
    return redirect(f'https://github.com/login/oauth/authorize?'
                    f'client_id={current_app.config.get("GITHUB_OAUTH_ID")}&'
                    f'response_type=code&'
                    f'redirect_uri={redirect_uri}&'
                    f'scope=user:email%20read:org%20repo')


@oauth.route('/github_oauth_callback')
def github_oauth_callback():
    pass


@oauth.route('/bitbucket_oauth_handshake', methods=['GET'])
def bitbucket_oauth_handshake():
    if not current_user.is_anonymous and current_user.bitbucket_id is not None:
        return redirect(url_for('index.home'))
    redirect_uri = url_for('oauth.bitbucket_oauth_callback', _external=True)
    return redirect(f'https://bitbucket.org?'
                    f'client_id={current_app.config.get("BITBUCKET_OAUTH_ID")}&'
                    f'response_type=code&'
                    f'redirect_uri={redirect_uri}&'
                    f'state=state')


@oauth.route('/bitbucket_oauth_callback')
def bitbucket_oauth_callback():
    pass


@oauth.route('/gitlab_oauth_handshake', methods=['GET'])
def gitlab_oauth_handshake():
    if not current_user.is_anonymous and current_user.gitlab_id is not None:
        return redirect(url_for('index.home'))
    redirect_uri = url_for('oauth.gitlab_oauth_callback')
    return redirect(f'https://gitlab.com/oauth/authorize?'
                    f'response_type=code&'
                    f'redirect_uri={redirect_uri}&'
                    f'state=state')


@oauth.route('/gitlab_oauth_callback')
def gitlab_oauth_callback():
    pass
