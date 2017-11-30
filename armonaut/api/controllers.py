from flask import abort, Blueprint, jsonify, request
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
    return jsonify(project=project_to_json(project))


@api.route('/projects/<string:host>/<string:owner>/<string:name>/builds', methods=['GET'])
def search_builds(host, owner, name):
    try:
        count = min(max(int(request.args.get('count', 50)), 50), 1)
    except TypeError:
        return jsonify(message='Parameter `count` must be an integer'), 400
    try:
        page = min(int(request.args.get('page', 1)), 1)
    except TypeError:
        return jsonify(message='Parameter `page` must be an integer'), 400
    branch = request.args.get('branch', None)
    status = request.args.get('status', None)
    if status not in STATUSES:
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

    query = Build.query.filter(Build.project_id == project.id).order_by(Build.start_time)
    if branch is not None:
        query = query.filter(Build.commit_branch == branch)
    if status is not None:
        query = query.filter(Build.status == status)
    if pull_request is not None:
        query = query.filter(Build.pull_request_number == pull_request)
    builds = query.offset((page - 1) * count).limit(count).all()

    return jsonify(builds=[build_to_json(build, project) for build in builds])


@api.route('/projects/<string:host>/<string:owner>/<string:name>/builds/<int:build_number>', methods=['GET'])
def get_build(host, owner, name, build_number):
    project = Project.query.filter(Project.remote_host == host,
                                   Project.owner == owner,
                                   Project.name == name).first()
    if project is None:
        return abort(404)
    build = Build.query.filter(Build.project_id == project.id,
                               Build.number == build_number).first()
    if build is None:
        return abort(404)
    return jsonify(build=build_to_json(build, project))


def project_to_json(project: Project, latest_build: Build=None):
    if latest_build is None:
        latest_build = project.latest_build
    return {
        'id': project.id,
        'name': project.name,
        'owner': project.owner,
        'slug': project.slug,
        'remote_host': project.remote_host,
        'remote_id': project.remote_id,
        'remote_url': project.remote_url,
        'url': f'https://armonaut.io/{project.remote_host}/{project.owner}/{project.name}',
        'default_branch': project.default_branch,
        'private': project.private,
        'latest_build': {
            'id': latest_build.id,
            'number': latest_build.number,
            'state': latest_build.state,
            'duration': latest_build.duration,
            'start_time': strftime(latest_build.start_time),
            'finish_time': strftime(latest_build.finish_time)
        } if latest_build is not None else None
    }


def build_to_json(build: Build, project: Project=None):
    if project is None:
        project = build.project
    return {
        'id': build.id,
        'number': build.number,
        'duration': build.duration,
        'start_time': strftime(build.start_time),
        'finish_time': strftime(build.finish_time),
        'status': build.status,
        'commit': {
            'branch': build.commit_branch,
            'url': build.commit_url,
            'sha': build.commit_sha,
            'tag': build.commit_tag,
            'author': build.commit_author
        },
        'pull_request': {
            'number': build.pull_request_number,
            'slug': build.pull_request_slug,
            'branch': build.pull_request_branch,
            'url': build.pull_request_url
        } if build.pull_request_number is not None else None,
        'project': project_to_json(project),
        'jobs': [job_to_json(job) for job in build.jobs]
    }


def job_to_json(job: Job):
    return {
        'id': job.id,
        'number': job.number,
        'status': job.status,
        'start_time': strftime(job.start_time),
        'finish_time': strftime(job.finish_time),
        'duration': job.duration,
        'container_units': job.container_units,
        'pool': {
            'id': job.pool.id,
            'community': job.pool.community
        }
    }


def strftime(dt) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%SZ')
