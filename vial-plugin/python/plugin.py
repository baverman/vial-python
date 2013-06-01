from vial import vfunc, vim
from vial.utils import get_var

from . import env

def python_buffer(buf):
    vfunc.setbufvar(buf.number, '&omnifunc', 'VialPythonOmni')

def omnifunc():
    lvars = vim.bindeval('a:')
    if lvars['findstart']:
        lvars['result'] = vim.current.window.cursor[1] - 1
    else:
        lvars['result'] = ['boo', 'foo']

def executable_choice():
    executables = set(('default', 'python2', 'python3'))\
        .union(env.get_virtualenvwrapper_executables())\
        .union(get_var('vial_python_executables', {}))

    vim.bindeval('a:')['result'] = '\n'.join(sorted(executables))

def set_executable(name):
    vim.vars['vial_python_executable'] = name
