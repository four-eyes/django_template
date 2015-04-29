from fabric.api import env, run, prefix
from fabric.contrib.project import rsync_project

env.roledefs = {
    'production': ['root@production'],
    'staging': ['root@staging'],
}

RSYNC_EXCLUDES = ['local_settings.py', '.git', '*.pyc', 'htmlcov', 'mediafiles', 'server', 'celerybeat-schedule', 'node_modules', '__pycache__']


def rsync():
    rsync_project(remote_dir='/opt/{{ project_name }}', exclude=RSYNC_EXCLUDES, delete=True)


def install_dependencies():
    with prefix('source /opt/{{ project_name }}/venv/bin/activate'):
        run('/opt/{{ project_name }}/venv/bin/pip install -r /opt/{{ project_name }}/{{ project_name }}/requirements.txt -U')


def create_virtualenv():
    run('virtualenv --python=python3 /opt/{{ project_name }}/venv')


def install():
    create_virtualenv()
    deploy()


def syncdb():
    with prefix('source /opt/{{ project_name }}/venv/bin/activate'):
        run('/opt/{{ project_name }}/venv/bin/python /opt/{{ project_name }}/{{ project_name }}/manage.py syncdb')


def collect_static():
    with prefix('source /opt/{{ project_name }}/venv/bin/activate'):
        run('/opt/{{ project_name }}/venv/bin/python /opt/{{ project_name }}/{{ project_name }}/manage.py collectstatic --noinput --settings {{ project_name }}.settings')


def deploy():
    rsync()
    install_dependencies()
    syncdb()
    collect_static()
    run('supervisorctl restart {{ project_name }}')
