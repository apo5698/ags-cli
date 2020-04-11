from datetime import date
import os

import yaml

import agsmsg as msg


def current_semester():
    """ Return the current semester.\n
    Format: `yyyy-semester`. For example: 2019-fall, 2020-spring
    """

    today = date.today()
    semester = "spring" if 1 <= today.month <= 4 else "fall"
    return f"{today.year}-{semester}"


__global_config__ = []
__assignment_config__ = {}


def read_config_glob(config="config/config.yaml"):
    """ Read config.yaml and return a list containing links for assignments
    and other settings. Links are at index 0, settings are at index 1.
    """

    temp = []
    with open(config, "r") as f:
        conf_yaml = yaml.load(f, Loader=yaml.FullLoader)
        for item in conf_yaml.values():
            temp.append(item)

    links = temp[0]
    for li in links:
        if li.startswith("p"):
            links[li] = links.get(li).replace("%SEMESTER%", current_semester())
    settings = temp[1]

    global __global_config__
    __global_config__ = [links, settings]


def read_config_asmt(config: str):
    """ Read the config of the assignment. """

    global __assignment_config__
    if not os.path.exists(config):
        msg.warn(f'{config} not found. Loading default config...')
        config = f'{config.split("_")[0]}.yaml'

    with open(config, 'r') as f:
        assignment_config__ = yaml.load(f, Loader=yaml.FullLoader)


def get_link(assignment):
    """ Return the link to the assignment. """
    return __global_config__[0].get(assignment)


def conf_glob(setting):
    """ Return the value of an item in global settings. """
    return __global_config__[1].get(setting)


def conf_as(setting):
    """ Return the value of an item in assignment settings. """
    return __assignment_config__.get(setting)


def init(force):
    import shutil

    msg.info('Initializing...')
    if force:
        option = msg.ask_yn('Force initialize will possibly remove all files, '
                            'continue with <force> flag?',
                            msgtype='warn')
        if not option:
            force = False

    dirs = ['content',
            'content/exercises', 'content/projects', 'content/homework']
    for d in dirs:
        if os.path.exists(d) and force:
            shutil.rmtree(d, ignore_errors=True)
        os.mkdir(d)
    # Day 1 to 27
    for i in range(1, 28):
        d = f'content/exercises/day{str(i).zfill(2)}'
        if os.path.exists(d) and force:
            shutil.rmtree(d, ignore_errors=True)
        os.mkdir(d)
    # Day 1 to 6
    for i in range(1, 7):
        d = f'content/projects/p{str(i)}'
        if os.path.exists(d) and force:
            shutil.rmtree(d, ignore_errors=True)
        os.mkdir(d)
    # Day 1 to 4
    for i in range(1, 5):
        d = f'content/homework/hw{str(i)}'
        if os.path.exists(d) and force:
            shutil.rmtree(d, ignore_errors=True)
        os.mkdir(d)

    msg.info('Done')
