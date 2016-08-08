import re
import os
import sys
from functools import partial

import paramiko


BASE_DIR = '/'.join((os.path.realpath(__file__)).split('/')[:-1])
SYNC_INGORE = ['__pycache__', 'Makefile.settings', 'Makefile', '.DS_Store', '.db', '.pyc']
SYNC_INGORE_FOLDERS = ['.git', '.idea', 'server']

# base validation
if len(sys.argv) < 2:
    raise Exception('Missing arguments <server type> [ssh_key_path]')

# process calls
action = None
ssh_key = None

for arg in sys.argv:
    if arg.find('=') != -1:
        name, value = arg.split('=')
        if name == '--ssh_key':
            ssh_key = value
        if name == '--action':
            action = value

if not action:
    raise Exception('--action=<action> should be provided')

server_type = sys.argv[1]


def is_ignored(file_name, root=True):
    # if path with ignored forder or ignored single filename, return True
    if (file_name.find('/') != -1 and any([i in SYNC_INGORE_FOLDERS for i in file_name.split('/')]) or
            any([file_name.endswith(ignore) for ignore in SYNC_INGORE])):
        return True
    elif root and file_name in SYNC_INGORE_FOLDERS:
        return True
    return False


def sync(client):
    """
    Recursive file copy
    """
    sftp = client.open_sftp()
    try:
        sftp.mkdir(remote_path)
    except OSError:
        pass
    for root, folders, fls in os.walk(BASE_DIR):
        if root.startswith(BASE_DIR):
            root = root[len(BASE_DIR):].strip('/')
        if is_ignored(root, root=True):
            continue
        for folder in folders:
            if is_ignored(folder):
                continue
            folder_path = os.path.join(remote_path, root, folder)
            try:
                print('Create folder: {}'.format(folder_path))
                sftp.mkdir(folder_path)
            except OSError:
                pass

        for file in fls:
            if is_ignored(file):
                continue
            file_path = os.path.join(remote_path, root, file)
            print('Copy file: {}'.format(file_path))
            try:
                sftp.put(os.path.join(BASE_DIR, root, file), file_path)
            except IOError:
                pass


def run_client_command(client, command, **kwargs):
    stdin, stdout, stderr = client.exec_command(command, **kwargs)
    stderr = '\n'.join([i.strip('\n') for i in stderr])
    if stderr:
        raise Exception(stderr)
    for line in stdout.readlines():
        print(line.strip('\n'))


def get_ansible_var(name, server_type=server_type):
    """
    Return variable or tuple from ansible var file
    """
    with open('./server/ansible/{}'.format(server_type), 'r') as f:
        read_vars = False
        for line in f.readlines():
            match = re.match(r'\w+@(\d+\.){3}\d+', line)
            if name == 'ssh_connect' and match:
                return match.group().split('@')  # return (user_name, host_ip, )
            if line.find('[{}:vars]'.format(server_type)) != -1:
                read_vars = True
                continue
            if read_vars and len(line.split('=')) == 2:
                var_name, value = line.split('=')
                if var_name == name:
                    return value.replace('\n', '')


# read ansible config variables
project_name = get_ansible_var('project_name')
project_folder_name = get_ansible_var('project_folder_name')
local_dir = './'
repo_name = get_ansible_var('repo_name')
host = get_ansible_var('host')
user_name, host_ip = get_ansible_var('ssh_connect')
remote_path = '/opt/{}/{}/'.format(project_folder_name, project_name)

# prepare client connection
client = paramiko.SSHClient()
if ssh_key:
    key = paramiko.RSAKey.from_private_key_file(ssh_key)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host_ip, username=user_name, pkey=key)
else:
    client.load_system_host_keys()
    client.connect(host_ip, username=user_name)
run = partial(run_client_command, client)


def task(func):
    if func.__name__ == action:
        print('Task:', func.__name__)
        func()
    return func


def create_virtualenv(client):
    print('Create venv')
    try:
        sftp = client.open_sftp()
        sftp.stat('/opt/{0}/venv/bin/python'.format(project_folder_name))
        return
    except IOError:
        pass
    run('mkdir -p /opt/{}'.format(project_folder_name))
    run('virtualenv --python=python3.4 /opt/{}/venv'.format(project_folder_name))


def install_dependencies():
    print('Install dependencies')
    run('/opt/{0}/venv/bin/pip install pip -U'.format(project_folder_name))
    run('/opt/{0}/venv/bin/pip install -r /opt/{0}/{1}/requirements.txt -U'.format(project_folder_name, repo_name))


@task
def import_db():
    run('cd /opt/{0}/{1} && /opt/{0}/venv/bin/python manager.py import_db'.format(project_folder_name, repo_name))


@task
def restart_app():
    run('sudo supervisorctl restart {}'.format(project_folder_name))


@task
def deploy():
    sync(client)
    create_virtualenv(client)
    install_dependencies()
    restart_app()


@task
def restart_all():
    run('sudo service supervisor stop')
    run('ps -Alf | grep "celery worker" | awk \'{print $4}\' | xargs kill -9')
    run('ps -Alf | grep "venv/bin/gunicorn" | awk \'{print $4}\' | xargs kill -9')
    run('sudo service supervisor start')

client.close()
