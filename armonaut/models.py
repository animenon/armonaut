from armonaut import BaseModel
import base64
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, SmallInteger
from sqlalchemy.orm import relationship
import typing


class Project(BaseModel):
    __tablename__ = 'projects'

    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)

    default_branch = Column(String, nullable=False, default='master')
    private = Column(Boolean, nullable=False)
    secret_env = Column(String, default=None)
    
    deploy_branch = Column(String, default='master')
    deploy_on = Column(String, default='tag')  # Options: tag, success, never

    builds = relationship('Build', back_populates='project')


class Build(BaseModel):
    __tablename__ = 'builds'

    start_time = Column(DateTime, nullable=False,
                        default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=None)

    # HEAD/Merge Commit
    commit_branch = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    commit_author = Column(String, nullable=False)
    commit_url = Column(String, nullable=False)
    commit_tag = Column(String, default=None)

    # Pull Request
    pull_request_number = Column(Integer, default=None)
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
    
    # Scheduling
    run_deploy = Column(Boolean, default=False, nullable=False)  # Only one job per build runs deploy.
    
    project = relationship('Project', back_populates='builds')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    jobs = relationship('Job', back_populates='build')

    @property
    def duration(self) -> float:
        """Returns the sum of all jobs that have started executing."""
        return sum([j.duration for j in self.jobs if j.start_time is not None])


class Job(BaseModel):
    __tablename__ = 'jobs'

    start_time = Column(DateTime, default=None)
    end_time = Column(DateTime, default=None)
    
    env = Column(String, default=None)
    container_id = Column(String(4), default=None)  # C2M, C2S, VC1L, or VC1M
    container_units = Column(SmallInteger, default=1, nullable=False)

    build = relationship('Build', back_populates='jobs')
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)

    @property
    def duration(self) -> typing.Union[None, float]:
        """Returns None if the job hasn't started yet, otherwise
        returns the number of seconds that the job has been running.
        """
        if self.start_time is None:
            return None
        end_time = self.end_time
        if end_time is None:
            end_time = datetime.datetime.utcnow()
        return (end_time - self.start_time).total_seconds()
    
    @property
    def queue_time(self) -> float:
        """Returns the number of seconds that this job has been in the queue."""
        start_time = self.start_time
        if self.start_time is None:
            self.start_time = datetime.datetime.utcnow()
        return (start_time - self.create_time).total_seconds()
    
    def resolve_env(self) -> typing.Dict[str, str]:
        """Resolves all values for this job's environment variables
        from all sources. Also includes the project-level `secret_env`
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

def unpack_string_list(value: str) -> typing.List[str]:
    """Unpacks a list of strings that has been packed as
    a NUL-separated list and then base64-encoded
    """
    if value is None or value == '':
        return []
    return [x.decode('utf-8') for x in base64.b64decode(value.encode('ascii')).split(b'\x00')]


def unpack_string_dict(value: str) -> typing.Dict[str, str]:
    dct = {}
    lst = unpack_tring_list(value)
