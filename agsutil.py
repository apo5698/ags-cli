from datetime import date

import yaml


def __current_semester__():
    """ Return the current semester.\n
    Format: `yyyy-semester`. For example: 2019-fall, 2020-spring
    """
    today = date.today()
    semester = "spring" if 1 <= today.month <= 4 else "fall"
    return f"{today.year}-{semester}"


def __read_config__(config="config.yaml"):
    """ Read config.yaml and return a list containing links for assignments
    and other settings. Links are at index 0, settings are at index 1.
    """

    temp = []
    with open(config, "r") as f:
        conf_yaml = yaml.load(f, Loader=yaml.FullLoader)
        for item in conf_yaml.values():
            temp.append(item)

    exercises = list(temp[0][0].values())
    proj = list(temp[0][1].values())
    projects = [None]
    # Skipped proj[0] (None)
    for p in proj[1:]:
        projects.append(p.replace("%SEMESTER%", __current_semester__()))
    homework = list(temp[0][2].values())
    settings = temp[1]

    return [[exercises, projects, homework], settings]


__global_config__ = __read_config__()


def get_link(category, num):
    """ Return the link to the assignment. """

    return __global_config__[0][category][num]


def get_setting(setting):
    """ Return the value of any item in settings. """

    return __global_config__[1].get(setting)
