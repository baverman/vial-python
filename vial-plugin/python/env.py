import os
import sys
import tempfile

from os.path import exists, join, expanduser, isdir, realpath
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
        return sys.executable
    elif name == 'python2':
        path = which('python2')
        if path:
            return path
    elif name == 'python3':
        path = which('python3')
        if path:
            return path

    return sys.executable


def get_executable_v():
    return get_executable()


def get():
    executable = get_executable()

    try:
        env = environments[executable]
    except KeyError:
        logfile = join(tempfile.gettempdir(), 'supp.log')
        env = environments[executable] = Environment(executable,
            get_var('vial_python_executable_env', {}), logfile)

    return env

def close_all():
    for v in environments.values():
        v.close()
