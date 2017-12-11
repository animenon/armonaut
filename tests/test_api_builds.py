import datetime
import pytest
from flask import url_for
from armonaut.models import Build


def test_api_get_builds(app, session, client, project):
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

    r = client.get(url_for('api.get_builds', host='gh', owner='armonaut', name='armonaut'), query_string={'branch': 'master'})
    assert r.status_code == 200
    assert len(r.json['builds']) == 2
    assert r.json['builds'] == [x.build_to_json() for x in [build2, build1]]

    r = client.get(url_for('api.get_build', host='gh', owner='armonaut', name='armonaut', build_number=1))
    assert r.status_code == 200
    assert r.json['build'] == build1.build_to_json()


@pytest.mark.parametrize('query_string', [{'count': 'a'}, {'page': 'a', 'count': '5'}, {'pull_request': 'a'}, {'status': 'unknown'}])
def test_api_builds_bad_query_string(app, session, client, project, query_string):
    build1 = Build()
    build1.project = project
    build1.number = 1
    build1.commit_branch = 'master'
    build1.commit_sha = '1'
    build1.commit_author = 'a@b'
    build1.commit_url = 'https://url'
    build1.start_time = datetime.datetime(2017, 1, 1, 0, 0, 0)

    session.add(build1)
    session.commit()

    r = client.get(url_for('api.get_builds', host='gh', owner='armonaut', name='armonaut'), query_string=query_string)

    assert r.status_code == 400
    assert 'message' in r.json


@pytest.mark.parametrize('query_string,expected_number', [({'branch': 'master'}, 2),
                                                          ({'pull_request': '1'}, 1),
                                                          ({'status': 'success'}, 1)])
def test_api_builds_filter(app, session, client, project, query_string, expected_number):
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
    build2.status = 'success'
    build2.start_time = datetime.datetime(2017, 1, 1, 0, 0, 1)

    build3 = Build()
    build3.project = project
    build3.number = 3
    build3.commit_branch = 'not-master'
    build3.commit_sha = '3'
    build3.commit_author = 'a@b'
    build3.commit_url = 'https://url'
    build3.pull_request_number = 1
    build3.pull_request_url = 'https://url'
    build3.pull_request_branch = 'master'
    build3.pull_request_slug = 'different/armonaut.io'
    build3.start_time = datetime.datetime(2017, 1, 1, 0, 0, 1)

    session.add(project)
    session.add(build1)
    session.add(build2)
    session.add(build3)
    session.commit()

    r = client.get(url_for('api.get_builds', host='gh', owner='armonaut', name='armonaut'), query_string=query_string)

    assert r.status_code == 200
    assert len(r.json['builds']) == expected_number
