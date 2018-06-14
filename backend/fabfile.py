import datetime
import os

from fabric.api import cd, env, local, run
from fabric.colors import cyan, green

DB_DUMP_FILENAME = 'ddiy.dump'
RSYNC_EXCLUDES = ['local_settings.py', '.git/', 'db.sqlite3']


# ==============================================================================
# ENVIRONMENTS
# ==============================================================================
def prod():
    env.use_ssh_config = True
    env.user = 'deploy'
    env.hostname = 'ddiy-prod'
    env.hosts = [env.hostname]
    env.key_filename = '~/.ssh/ddiy-solutions/t2micro-EC2-instance.pem'
    env.branch = 'master'
    env.git_source = '~/src/git_repo'
    env.django_source = '~/src/git_repo/backend/'
    env.django_destination = '~/project/'
    env.db_file_path = '~/project/db.sqlite3'
    env.db_backup_dir = '~/backups/sqlite/'
    env.wsgi_file = '~/project/backend/wsgi.py'


# ==============================================================================
# SUB TASKS
# ==============================================================================
def run_collectstatic():
    """Runs `./manage.py collectstatic` on the server."""
    print(cyan('\n➜  run_collectstatic'))
    with cd(env.django_destination):
        run('pipenv run ./manage.py collectstatic --noinput')


def run_dump_db(filename=None):
    """Saves a backup of the database into the backup folder."""
    print(cyan('\n➜  run_dump_db'))
    if filename is None:
        filename = DB_DUMP_FILENAME
    run('cp {} {}{}'.format(env.db_file_path, env.db_backup_dir, filename))


def run_git_pull(branch='master'):
    """
    Revokes all changes on the remote repo and then pulls the latest code.

    There are never supposed to be any changes on the repo. The revoking is
    just a safety net to avoid any conflicts/merges while pulling.

    """
    print(cyan('\n➜  run_git_pull'))
    with cd('%s' % env.git_source):
        # UNDO all changes that might have happened in the repo
        run('git checkout .')
        run('git clean -f')

        # Pull latest code
        run("git checkout %s" % branch)
        run("git pull --no-edit origin %s" % branch)
        run("git submodule init")
        run("git submodule update")


def run_pipenv_install():
    """Runs `pipenv install` on the server."""
    print(cyan('\n➜  run_pipenv_install'))
    with cd(env.django_destination):
        run('pipenv install')


def run_migrate():
    """Runs `./manage.py migrate` on the server."""
    print(cyan('\n➜  run_migrate'))
    run_dump_db(filename=datetime.datetime.now().isoformat())
    with cd(env.django_destination):
        run('pipenv run ./manage.py migrate')


def run_rsync_backend():
    """
    Copies the project from the git repository to it's destination folder.

    This has the nice side effect of rsync deleting all ``.pyc`` files and
    removing other files that might have been left behind by sys admins messing
    around on the server.

    """
    print(cyan('\n➜  run_rsync_project'))
    excludes = ''
    for exclude in RSYNC_EXCLUDES:
        excludes += " --exclude '{0}'".format(exclude)
    command = "rsync -avz --stats --delete {0} {1} {2}".format(
        excludes, env.django_source, env.django_destination)
    run(command)


def run_touch_wsgi():
    """Touches the wsgi file."""
    print(cyan('\n➜  run_touch_wsgi'))
    run('touch {0}'.format(env.wsgi_file))


# ==============================================================================
# MAIN TASKS
# ==============================================================================
def run_deploy():
    """Runs a Django deployment."""
    print(cyan('\n➜  run_deploy'))
    run_git_pull(env.branch)
    run_rsync_backend()
    run_pipenv_install()

    # ATTENTION: If you comment out `run_migrate`, execute `run_dump_db`
    # here!!!
    run_migrate()

    run_collectstatic()
    run_touch_wsgi()
    print(green('\n➜  Deployment succesful!'))


def test_cypress():
    local('rm -rf cypress_test_db')
    local(
        'pipenv run ./manage.py migrate --run-syncdb --settings=backend.cypress_settings'
    )
    local(
        'pipenv run ./manage.py create_cleaning_request_cypress_fixtures --settings=backend.cypress_settings'
    )
    local(
        'pipenv run ./manage.py runserver --settings=backend.cypress_settings')
