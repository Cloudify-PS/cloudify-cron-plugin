import os

from fabric.api import settings, run, put

from cloudify import ctx


config = '%(minute)s %(hour)s %(day_of_month)s %(month)s %(day_of_week)s ' \
         '%(script_target_path)s'
BASE_DIR = '/opt/cron'


def get_target_script_path(script_target_path):
        return os.path.join(BASE_DIR, os.path.basename(script_target_path))


def copy_script_file(script_target_path):
    tmpfile = ctx.download_resource_and_render(script_target_path)
    target_script_path = get_target_script_path(script_target_path)
    put(tmpfile, tmpfile)
    run('sudo mv {0} {1}'.format(tmpfile, target_script_path))
    return target_script_path


def create_cron_file(cron_file_path, cron_script_path):
    properties = dict.copy(ctx.node.properties)
    properties['script_target_path'] = cron_script_path
    updated_config = config % properties
    run('sudo tee -a {0} <<EOF \n{1}\nEOF'.format(cron_file_path,
                                                  updated_config))


def create(fabric_env, target_cron_path, **kwargs):
    with settings(**fabric_env):
        run('sudo mkdir -p {0}'.format(BASE_DIR))
        target_script_path = copy_script_file(
            ctx.node.properties['script_path'])
        run('sudo chmod +x {0}'.format(target_script_path))
        create_cron_file(target_cron_path, target_script_path)


def delete(fabric_env, target_cron_path, **kwargs):
    with settings(**fabric_env):
        target_script_path = get_target_script_path(
            ctx.node.properties['script_path'])
        run('sudo rm {0}'.format(target_script_path))
        run('sudo rm {0}'.format(target_cron_path))

