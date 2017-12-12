import requests
import uuid
from flask import url_for
from armonaut import __version__, db
from armonaut.models import Project


class GithubProject(Project):
    __mapper_args__ = {'polymorphic_identity': 'gh'}

    def has_webhook(self) -> bool:
        if self.webhook_id is not None:
            with requests.head(f'https://api.github.com/repos/{self.owner}/{self.name}/hooks/{self.webhook_id}',
                               headers={'Authorization': f'token {self.account.github_access_token}',
                                        'User-Agent': f'Armonaut/{__version__}',
                                        'Accept': 'application/vnd.github.v3+json'}) as r:
                if r.status_code == 401:
                    db.session.add(self.account)
                    self.account.github_access_token = None
                    db.session.commit()
                return r.ok

    def create_webhook(self):
        if self.has_webhook():
            self.delete_webhook()
        db.session.add(self)
        self.webhook_secret = uuid.uuid4().hex
        with requests.post(f'https://api.github.com/repos/{self.owner}/{self.name}/hooks',
                           headers={'Authorization': f'token {self.account.github_access_token}',
                                    'User-Agent': f'Armonaut/{__version__}',
                                    'Accept': 'application/vnd.github.v3+json'},
                           json={'name': 'web',
                                 'active': True,
                                 'events': ['push', 'pull_request', 'project'],
                                 'config': {'url': url_for('webhooks.github_webhooks'),
                                            'insecure_ssl': True,
                                            'secret': self.webhook_secret,
                                            'content_type': 'json'}}) as r:
            if r.status_code == 401:
                db.session.add(self.account)
                self.account.github_access_token = None
                db.session.commit()
            elif r.ok:
                self.active = True
                self.webhook_id = str(r.json()['id'])
            else:
                self.webhook_secret = None

        db.session.commit()

    def delete_webhook(self):
        if self.webhook_id is not None:
            with requests.delete(f'https://api.github.com/repos/{self.owner}/{self.name}/hooks/{self.webhook_id}',
                                 headers={'Authorization': f'token  {self.account.github_access_token}',
                                          'User-Agent': f'Armonaut/{__version__}',
                                          'Accept': 'application/vnd.github.v3+json'}) as r:
                if r.status_code == 401:
                    db.session.add(self.account)
                    self.account.github_access_token = None
                    db.session.commit()
                elif r.ok:
                    db.session.add(self)
                    self.active = False
                    self.webhook_id = None
                    self.webhook_secret = None
                    db.session.commit()

    def update_commit_status(self, commit, status, url):
        commit_status = None
        description = None
        if status == 'running':
            commit_status = 'pending'
            description = 'The Armonaut build is running'
        elif status == 'success':
            commit_status = 'success'
            description = 'The Armonaut build passed'
        elif status == 'failure' or status == 'canceled':
            commit_status = 'failure'
            description = 'The Armonaut build failed'
        elif status == 'error':
            commit_status = 'error'
            description = 'The Armonaut build encountered an error'
        if commit_status is not None:
            with requests.post(f'https://api.github.com/repos/{self.owner}/{self.name}/statuses/{commit}',
                               headers={'Authorization': f'token  {self.account.github_access_token}',
                                        'User-Agent': f'Armonaut/{__version__}',
                                        'Accept': 'application/vnd.github.v3+json'},
                               json={'state': commit_status,
                                     'target_url': url,
                                     'description': description,
                                     'context': 'continuous-integration/armonaut'}) as r:
                if r.status_code == 401:
                    db.session.add(self.account)
                    self.account.github_access_token = None
                    db.session.commit()

    def sync_project(self):
        with requests.get(f'https://api.github.com/repos/{self.owner}/{self.name}',
                          headers={'Authorization': f'token  {self.account.github_access_token}',
                                   'User-Agent': f'Armonaut/{__version__}',
                                   'Accept': 'application/vnd.github.v3+json'}) as r:
            if r.status_code == 401:
                db.session.add(self.account)
                self.account.github_access_token = None
                db.session.commit()
            elif r.ok:
                repo_info = r.json()
                db.session.add(self)
                self.owner = repo_info['owner']['login']
                self.name = repo_info['name']
                self.default_branch = repo_info['default_branch']
                self.private = repo_info['private']
                db.session.commit()
