import os
import sys
import tempfile

from os.path import exists, join, expanduser, isdir, realpath

try:
    import supp
except ImportError:
    fname = os.__file__
    if fname.endswith('.pyc'):
        fname = fname[:-1]

    if not os.path.islink(fname):
        raise

    real_prefix = os.path.dirname(os.path.realpath(fname))
    site_packages = os.path.join(real_prefix, 'site-packages')
    egg_link = os.path.join(site_packages, 'supp.egg-link')
    if os.path.exists(egg_link):
        site_packages = open(egg_link).readline().strip()

    old_path = sys.path
    sys.path = old_path + [site_packages]
    try:
        import supp
    finally:
        sys.path = old_path

from supp.remote import Environment

from vial.utils import get_var

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
    name = get_var('vial_python_executable', 'default')

    try:
        return get_var('vial_python_executables', {})[name]
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
            for r in get_var('vial_python_sources', [os.getcwd()])]


def get():
    executable = get_executable()
    try:
        env = environments[executable]
    except KeyError:
        logfile = join(tempfile.gettempdir(), 'supp.log')
        dyn_modules = list(get_var('vial_python_dynamic', []))
        env = Environment(executable,
                          get_var('vial_python_executable_env', {}), logfile)
        env.configure({'sources': get_sources(), 'dyn_modules': dyn_modules})
        environments[executable] = env

    return env


def close_all():
    for v in environments.values():
        v.close()
