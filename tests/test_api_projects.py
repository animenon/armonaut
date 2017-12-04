import pytest
from flask import url_for
from armonaut.models import Project


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
