import os
import sys
import site
import tempfile

from os.path import exists, join, expanduser, isdir, realpath

try:
    import supp
except ImportError:
    sites = []
    new_path = []

    user_site = getattr(site, 'USER_SITE')
    if user_site:
        sites.append(user_site)

    os_fname = os.__file__
    if os_fname.endswith('.pyc'):
        os_fname = os_fname[:-1]
    real_prefix = os.path.dirname(os.path.realpath(os_fname))
    sites.append(os.path.join(real_prefix, 'site-packages'))

    for site in sites:
        egg_link = os.path.join(site, 'supp.egg-link')
        if os.path.exists(egg_link):
            new_path.append(open(egg_link).readline().strip())
        new_path.append(site)

    old_path = sys.path
    sys.path = old_path + new_path
    try:
        import supp
    finally:
        sys.path = old_path


from supp.remote import Environment

from vial.compat import sstr
from vial.utils import get_var, get_list_var, get_dict_var

environments = {}

def which(binary_name):
    for p in os.environ.get('PATH', '').split(os.pathsep):
        path = join(p, binary_name)
        if exists(path):
            return path

    return None

def get_virtualenvwrapper_root():
    return realpath(os.getenv('WORKON_HOME', expanduser('~/.virtualenvs')))

def get_virtualenvwrapper_executables():
    root = get_virtualenvwrapper_root()
    result = {}
    if exists(root) and isdir(root):
        for p in os.listdir(root):
            epath = join(root, p, 'bin', 'python')
            if exists(epath):
                result[p] = epath

    return result

def get_virtualenvwrapper_executable(name):
    root = get_virtualenvwrapper_root()
    epath = join(root, name, 'bin', 'python')
    if exists(epath):
        return epath

def get_executable():
    name = sstr(get_var('vial_python_executable', 'default'))

    try:
        return get_dict_var('vial_python_executables')[name]
    except KeyError:
        pass

    path = get_virtualenvwrapper_executable(name)
    if path:
        return path

    if name == 'default':
        if 'VIRTUAL_ENV' in os.environ:
            return which('python')
        else:
            return which('python3')
    elif name == 'python2':
        path = which('python2')
        if path:
            return path
    elif name == 'python3':
        path = which('python3')
        if path:
            return path

    return sys.executable


def get_sources():
    return [os.path.normpath(os.path.abspath(r))
            for r in get_list_var('vial_python_sources', [os.getcwd()])]


def get():
    executable = get_executable()
    try:
        env = environments[executable]
    except KeyError:
        logfile = join(tempfile.gettempdir(), 'supp.log')
        dyn_modules = list(get_list_var('vial_python_dynamic'))
        env = Environment(executable,
                          get_dict_var('vial_python_executable_env'), logfile)
        env.configure({'sources': get_sources(), 'dyn_modules': dyn_modules})
        environments[executable] = env

    return env


def close_all():
    for v in environments.values():
        v.close()
