from vial import vfunc, vim
from vial.utils import get_var, vimfunction

from . import env

def python_buffer(buf):
    vfunc.setbufvar(buf.number, '&omnifunc', 'VialPythonOmni')

@vimfunction
def omnifunc(findstart, base):
    if findstart:
        return vim.current.window.cursor[1] - 1
    else:
        return ['boo', 'foo']

@vimfunction
def executable_choice(start, cmdline, pos):
    executables = set(('default', 'python2', 'python3'))\
        .union(env.get_virtualenvwrapper_executables())\
        .union(get_var('vial_python_executables', {}))

    return '\n'.join(sorted(executables))

def set_executable(name):
    vim.vars['vial_python_executable'] = name
