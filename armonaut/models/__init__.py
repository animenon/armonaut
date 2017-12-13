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

from armonaut import BaseModel, login
import base64
import datetime
import re
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, SmallInteger, BigInteger, func
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import typing

STATUSES = {'queued', 'starting', 'running', 'success', 'failure', 'error', 'canceled'}
_UNPACK_DICT_REGEX = re.compile(r'^([^\s=]+)=(.*)$')


class Account(BaseModel, UserMixin):
    __tablename__ = 'accounts'

    github_id = Column(BigInteger, default=None, index=True)
    github_login = Column(String, default=None)
    github_email = Column(String, default=None)
    github_access_token = Column(String, default=None)

    bitbucket_id = Column(String, default=None, index=True)
    bitbucket_login = Column(String, default=None)
    bitbucket_email = Column(String, default=None)
    bitbucket_access_token = Column(String, default=None)
    bitbucket_refresh_token = Column(String, default=None)

    gitlab_id = Column(BigInteger, default=None, index=True)
    gitlab_login = Column(String, default=None)
    gitlab_email = Column(String, default=None)
    gitlab_access_token = Column(String, default=None)
    gitlab_refresh_token = Column(String, default=None)

    projects = relationship('Project', back_populates='account')


@login.user_loader
def get_user(id):
    return Account.query.get(id)


class Project(BaseModel):
    __tablename__ = 'projects'

    owner = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)

    remote_host = Column(String(2), nullable=False, index=True)
    remote_id = Column(BigInteger, nullable=False)

    default_branch = Column(String, nullable=False, default='master')
    private = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False, default=False)

    secret_env = Column(String, default=None)
    webhook_id = Column(String, default=None)
    webhook_secret = Column(String, default=None)

    account = relationship('Account', uselist=False, back_populates='projects')
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    builds = relationship('Build', back_populates='project')

    __mapper_args__ = {'polymorphic_on': remote_host}

    @property
    def slug(self) -> str:
        return f'{self.owner}/{self.name}'

    @property
    def remote_url(self) -> str:
        if self.remote_host == 'gh':
            host = 'github.com'
        elif self.remote_host == 'gl':
            host = 'gitlab.com'
        else:
            host = 'bitbucket.org'
        return f'https://{host}/{self.slug}'

    @property
    def latest_build(self):
        return Build.query.filter(Build.project_id == self.id).order_by(Build.number.desc()).first()

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

    def project_to_json(self):
        latest_build = self.latest_build
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'slug': self.slug,
            'remote_host': self.remote_host,
            'remote_id': self.remote_id,
            'remote_url': self.remote_url,
            'url': f'https://armonaut.io/{self.remote_host}/{self.owner}/{self.name}',
            'default_branch': self.default_branch,
            'private': self.private,
            'latest_build': {
                'id': latest_build.id,
                'number': latest_build.number,
                'status': latest_build.status,
                'duration': latest_build.duration,
                'start_time': strftime(latest_build.start_time),
                'finish_time': strftime(latest_build.finish_time)
            } if latest_build is not None else None
        }


class Build(BaseModel):
    __tablename__ = 'builds'

    start_time = Column(DateTime, nullable=False,
                        default=datetime.datetime.utcnow)
    finish_time = Column(DateTime, default=None)
    number = Column(Integer, nullable=False, index=True)
    status = Column(String(8), nullable=False, index=True, default='queued')

    # HEAD/Merge Commit
    commit_branch = Column(String, nullable=False, index=True)
    commit_sha = Column(String, nullable=False)
    commit_author = Column(String, nullable=False)
    commit_url = Column(String, nullable=False)
    commit_tag = Column(String, default=None)

    # Pull Request
    pull_request_number = Column(Integer, default=None, index=True)
    pull_request_branch = Column(String, default=None)
    pull_request_slug = Column(String, default=None)
    pull_request_url = Column(String, default=None)

    # armonaut.yml
    env = Column(String, default=None)
    install = Column(String, default=None)
    script = Column(String, default=None)
    after_success = Column(String, default=None)
    after_failure = Column(String, default=None)
    after_script = Column(String, default=None)
    deploy = Column(String, default=None)
    services = Column(String, default=None)

    project = relationship('Project', back_populates='builds')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    jobs = relationship('Job', back_populates='build')

    def determine_status(self) -> str:
        """Returns the status of the Build which is determined by it's jobs statuses."""
        statuses = {}
        for job in self.jobs:
            if job.status == 'failure' or job.status == 'error':
                return 'failure'
            statuses.setdefault(job.status, 0)
            statuses[job.status] += 1
        if statuses.get('running', 0) or statuses.get('starting', 0):
            return 'running'
        elif statuses.get('queued', 0):
            return 'queued'
        return 'success'

    @property
    def duration(self) -> int:
        """Returns the sum of all jobs that have started executing."""
        return sum([j.duration for j in self.jobs if j.start_time is not None])

    def build_to_json(self, project: Project = None):
        if project is None:
            project = self.project
        return {
            'id': self.id,
            'number': self.number,
            'duration': self.duration,
            'start_time': strftime(self.start_time),
            'finish_time': strftime(self.finish_time),
            'status': self.status,
            'commit': {
                'branch': self.commit_branch,
                'url': self.commit_url,
                'sha': self.commit_sha,
                'tag': self.commit_tag,
                'author': self.commit_author
            },
            'pull_request': {
                'number': self.pull_request_number,
                'slug': self.pull_request_slug,
                'branch': self.pull_request_branch,
                'url': self.pull_request_url
            } if self.pull_request_number is not None else None,
            'models': project.project_to_json(),
            'jobs': [job.job_to_json() for job in self.jobs]
        }


class Job(BaseModel):
    __tablename__ = 'jobs'

    start_time = Column(DateTime, default=None)
    finish_time = Column(DateTime, default=None)
    number = Column(SmallInteger, nullable=False)
    env = Column(String, default=None)

    # DigitalOcean Droplet for debugging purposes
    droplet_id = Column(String, default=None)

    # queued, starting, running, success, failure, error, canceled
    status = Column(String(8), default='queued', nullable=False, index=True)

    build = relationship('Build', back_populates='jobs')
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)

    @property
    def spaces_log_url(self) -> str:
        """Returns the URL that the logs will be stored at for this job.
        """
        return f'https://armonaut.nyc3.digitaloceanspaces.com/{self.build.models.spaces_secret_id}/logs/{self.build.number}/{self.number}/logs.txt'

    @property
    def spaces_cache_url(self) -> str:
        """Returns the URL that the cache tarball will be stored
        at and retrieved from for this job. Caches aren't updated for
        failing jobs or pull request jobs.
        """
        return f'https://armonaut.nyc3.digitaloceanspaces.com/{self.build.models.spaces_secret_id}/caches/{self.build.commit_branch}.tar.gz'

    @property
    def duration(self) -> typing.Union[None, int]:
        """Returns None if the job hasn't started yet, otherwise
        returns the number of seconds that the job has been running.
        """
        if self.start_time is None:
            return None
        end_time = self.finish_time
        if end_time is None:
            end_time = datetime.datetime.utcnow()
        return int((end_time - self.start_time).total_seconds())

    @property
    def queue_time(self) -> int:
        """Returns the number of seconds that this job has been in the queue."""
        start_time = self.start_time
        if self.start_time is None:
            self.start_time = datetime.datetime.utcnow()
        return int((start_time - self.create_time).total_seconds())

    def resolve_env(self) -> typing.Dict[str, str]:
        """Resolves all values for this job's environment variables
        from all sources. Also includes the models-level `secret_env`
        if the job has not been triggered by a pull request.
        """
        env = {}
        for k, v in unpack_string_dict(self.build.env).items():
            env[k] = v
        for k, v in unpack_string_dict(self.env).items():
            env[k] = v
        if self.build.pull_request_number is None:
            for k, v in unpack_string_dict(self.build.project.secret_env).items():
                env[k] = v
        return env

    def job_to_json(self):
        return {
            'id': self.id,
            'number': self.number,
            'status': self.status,
            'start_time': strftime(self.start_time),
            'finish_time': strftime(self.finish_time),
            'duration': self.duration,
            'container_units': self.container_units,
            'pool': {
                'id': self.pool.id,
                'community': self.pool.community
            } if self.pool is not None else None
        }


def unpack_string_list(value: str) -> typing.List[str]:
    """Unpacks a list of strings that has been packed as
    a NUL-separated list and then base64-encoded
    """
    if value is None or value == '':
        return []
    return [x.decode('utf-8') for x in base64.b64decode(value.encode('ascii')).split(b'\x00')]


def unpack_string_dict(value: str) -> typing.Dict[str, str]:
    dct = {}
    lst = unpack_string_list(value)
    for item in lst:
        match = _UNPACK_DICT_REGEX.match(item)
        if match:
            dct[match.group(1)] = match.group(2)
    return dct


def strftime(dt) -> typing.Union[str, None]:
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%SZ')


from armonaut.models.github import GithubProject
from armonaut.models.gitlab import GitlabProject
from armonaut.models.bitbucket import BitbucketProject
