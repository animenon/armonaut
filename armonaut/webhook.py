from flask import Blueprint


webhooks = Blueprint('webhooks', __name__, '/webhooks')


@webhooks.route('/github', methods=['POST'])
def github_webhooks():
    raise NotImplementedError()


@webhooks.route('/gitlab', methods=['POST'])
def gitlab_webhooks():
    raise NotImplementedError()


@webhooks.route('/bitbucket', methods=['POST'])
def bitbucket_webhooks():
    raise NotImplementedError()
