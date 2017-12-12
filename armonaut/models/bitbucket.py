import requests
from armonaut import __version__, db
from armonaut.models import Project


class BitbucketProject(Project):
    __mapper_args__ = {'polymorphic_identity': 'bb'}

    def has_file(self, path: str) -> bool:
        raise NotImplementedError()

    def has_webhook(self) -> bool:
        raise NotImplementedError()

    def create_webhook(self):
        raise NotImplementedError()

    def delete_webhook(self):
        raise NotImplementedError()

    def update_commit_status(self, commit, status, url):
        raise NotImplementedError()

    def is_owner(self, id) -> bool:
        raise NotImplementedError()

    def is_collaborator(self, id) -> bool:
        raise NotImplementedError()

    def is_access_token_valid(self):
        raise NotImplementedError()

    def sync_project(self):
        raise NotImplementedError()
