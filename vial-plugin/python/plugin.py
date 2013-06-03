import os
from vial import vfunc, vim
from vial.utils import get_var, vimfunction

from . import env

def python_buffer(buf):
    vfunc.setbufvar(buf.number, '&omnifunc', 'VialPythonOmni')

last_result = None
@vimfunction
def omnifunc(findstart, base):
    global last_result
    if findstart:
        source, pos = get_source_and_offset()
        m, _ = last_result = env.get().assist(os.getcwd(), source, pos, vim.current.buffer.name)
        if m is not None:
            return vim.current.window.cursor[1] - len(m)
        else:
            return -1
    else:
        return last_result[1]

@vimfunction
def executable_choice(start, cmdline, pos):
    executables = set(('default', 'python2', 'python3'))\
        .union(env.get_virtualenvwrapper_executables())\
        .union(get_var('vial_python_executables', {}))

    return '\n'.join(sorted(executables))

def set_executable(name):
    vim.vars['vial_python_executable'] = name

def get_source_and_offset():
    source = '\n'.join(vim.current.buffer[:])
    line, pos = vim.current.window.cursor
    offset = vfunc.line2byte(line) + pos
    return source, offset
