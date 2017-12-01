import datetime
import pytest
from flask import url_for
from armonaut.models import Project, Build


def test_no_project_found(app, session, client):
    r = client.get(url_for('api.get_project', host='gh', owner='armonaut', name='armonaut.io'))
    assert r.status_code == 404


def test_project_found(app, session, client):
    project = Project()
    project.remote_host = 'gh'
    project.remote_id = 1
    project.owner = 'armonaut'
    project.name = 'armonaut.io'
    project.private = False
    session.add(project)
    session.commit()

    r = client.get(url_for('api.get_project', host='gh', owner='armonaut', name='armonaut.io'))
    assert r.status_code == 200


@pytest.mark.parametrize('host,owner,name', [('bb', 'armonaut', 'armonaut.io'),
                                             ('gh', 'armonau', 'armonaut.io'),
                                             ('gh', 'armonaut', 'armonaut.i')])
def test_project_not_found_wrong_params(app, session, client, host, owner, name):
    project = Project()
    project.remote_host = 'gh'
    project.remote_id = 1
    project.owner = 'armonaut'
    project.name = 'armonaut.io'
    project.private = False
    session.add(project)
    session.commit()

    r = client.get(url_for('api.get_project', host=host, owner=owner, name=name))
    assert r.status_code == 404


@pytest.mark.parametrize('host, hostname', [('gh', 'github.com'), ('gl', 'gitlab.com'), ('bb', 'bitbucket.org')])
def test_project_api_remote_url(app, session, client, host, hostname):

    project = Project()
    project.remote_host = host
    project.remote_id = 1
    project.owner = 'armonaut'
    project.name = 'armonaut.io'
    project.private = False
    session.add(project)
    session.commit()

    r = client.get(url_for('api.get_project', host=host, owner='armonaut', name='armonaut.io'))
    assert r.status_code == 200
    assert r.json['project']['remote_url'] == f'https://{hostname}/armonaut/armonaut.io'


def test_project_api_get_builds(app, session, client):
    project = Project()
    project.remote_host = 'gh'
    project.remote_id = 1
    project.owner = 'armonaut'
    project.name = 'armonaut.io'
    project.private = False

    build1 = Build()
    build1.project = project
    build1.number = 1
    build1.commit_branch = 'master'
    build1.commit_sha = '1'
    build1.commit_author = 'a@b'
    build1.commit_url = 'https://url'
    build1.start_time = datetime.datetime(2017, 1, 1, 0, 0, 0)

    build2 = Build()
    build2.project = project
    build2.number = 2
    build2.commit_branch = 'master'
    build2.commit_sha = '2'
    build2.commit_author = 'a@b'
    build2.commit_url = 'https://url'
    build2.start_time = datetime.datetime(2017, 1, 1, 0, 0, 1)

    build3 = Build()
    build3.project = project
    build3.number = 3
    build3.commit_branch = 'not-master'
    build3.commit_sha = '3'
    build3.commit_author = 'a@b'
    build3.commit_url = 'https://url'
    build3.start_time = datetime.datetime(2017, 1, 1, 0, 0, 1)

    session.add(project)
    session.add(build1)
    session.add(build2)
    session.add(build3)
    session.commit()

    assert len(project.builds) == 3

    r = client.get(url_for('api.get_builds', host='gh', owner='armonaut', name='armonaut.io'), query_string={'branch': 'master'})
    assert r.status_code == 200
    assert len(r.json['builds']) == 2
    assert r.json['builds'] == [x.build_to_json() for x in [build2, build1]]
