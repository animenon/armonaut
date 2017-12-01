from flask import Blueprint, jsonify, request
from flask_login import current_user
from armonaut import limiter
from armonaut.models import Project, Build, Job, STATUSES


def api_rate_limit_func() -> str:
    if current_user.is_anonymous:
        return '60/hour'
    else:
        return '1000/hour'


api = Blueprint('api', __name__, url_prefix='/api/v1')
limiter.limit(api_rate_limit_func)(api)


@api.route('/projects/<string:host>/<string:owner>/<string:name>', methods=['GET'])
def get_project(host, owner, name):
    """Gets information about a project"""
    project = Project.query.filter(Project.remote_host == host,
                                   Project.owner == owner,
                                   Project.name == name).first()
    if project is None:
        return jsonify(message='Could not find a project with those parameters'), 404
    return jsonify(project=project.project_to_json())


@api.route('/projects/<string:host>/<string:owner>/<string:name>/builds', methods=['GET'])
def get_builds(host, owner, name):
    try:
        count = max(min(int(request.args.get('count', 50)), 50), 1)
    except TypeError:
        return jsonify(message='Parameter `count` must be an integer'), 400
    try:
        page = min(int(request.args.get('page', 1)), 1)
    except TypeError:
        return jsonify(message='Parameter `page` must be an integer'), 400
    branch = request.args.get('branch', None)
    status = request.args.get('status', None)
    if status is not None and status not in STATUSES:
        return jsonify(message='Parameter `status` must be a valid status string'), 400
    pull_request = request.args.get('pull_request', None)
    if pull_request is not None:
        try:
            pull_request = int(pull_request)
        except TypeError:
            return jsonify(message='Parameter `pull_request` must be an integer'), 400

    project = Project.query.filter(Project.remote_host == host,
                                   Project.owner == owner,
                                   Project.name == name).first()
    if project is None:
        return jsonify(message='Could not find a project with those parameters'), 404

    query = Build.query.filter(Build.project_id == project.id).order_by(Build.start_time.desc())
    if branch is not None:
        query = query.filter(Build.commit_branch == branch)
    if status is not None:
        query = query.filter(Build.status == status)
    if pull_request is not None:
        query = query.filter(Build.pull_request_number == pull_request)
    builds = query.offset((page - 1) * count).limit(count).all()

    return jsonify(builds=[build.build_to_json(project) for build in builds])


@api.route('/projects/<string:host>/<string:owner>/<string:name>/builds/<int:build_number>', methods=['GET'])
def get_build(host, owner, name, build_number):
    project = Project.query.filter(Project.remote_host == host,
                                   Project.owner == owner,
                                   Project.name == name).first()
    if project is None:
        return jsonify(message='Could not find a project with those parameters'), 404
    build = Build.query.filter(Build.project_id == project.id,
                               Build.number == build_number).first()
    if build is None:
        return jsonify(message='Could not find a build with those parameters'), 404
    return jsonify(build=build.build_to_json(project))
