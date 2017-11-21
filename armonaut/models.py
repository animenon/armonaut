from armonaut import BaseModel
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship


class Project(BaseModel):
    __tablename__ = 'projects'

    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)

    default_branch = Column(String, nullable=False, default='master')
    private = Column(Boolean, nullable=False)

    builds = relationship('Build', back_populates='project')


class Build(BaseModel):
    __tablename__ = 'builds'

    start_time = Column(DateTime, nullable=False,
                        default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=None)

    commit_branch = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    commit_author = Column(String, nullable=False)
    commit_url = Column(String, nullable=False)

    pull_request_number = Column(Integer, default=None)
    pull_request_branch = Column(String, default=None)
    pull_request_slug = Column(String, default=None)
    pull_request_url = Column(String, default=None)

    project = relationship('Project', back_populates='builds')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    jobs = relationship('Job', back_populates='build')

    @property
    def duration(self) -> float:
        end_time = self.end_time
        if end_time is None:
            end_time = datetime.datetime.utcnow()
        return (end_time - self.start_time).total_seconds()


class Job(BaseModel):
    __tablename__ = 'jobs'

    start_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, default=None)

    build = relationship('Build', back_populates='jobs')
    build_id = Column(Integer, ForeignKey('builds.id'), nullable=False)

    @property
    def duration(self) -> float:
        end_time = self.end_time
        if end_time is None:
            end_time = datetime.datetime.utcnow()
        return (end_time - self.start_time).total_seconds()
