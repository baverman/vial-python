import os
import re

from time import time

from vial import vfunc, vim, outline
from vial.utils import get_var, vimfunction, get_content_and_offset, get_content, \
    redraw, get_projects
from vial.fsearch import get_files

from . import env

def python_buffer(buf):
    vfunc.setbufvar(buf.number, '&omnifunc', 'VialPythonOmni')

last_result = None
@vimfunction
def omnifunc(findstart, base):
    global last_result
    if findstart:
        source, pos = get_content_and_offset()
        m, _ = last_result = env.get().assist(os.getcwd(), source, pos, 
            vim.current.buffer.name)
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


def goto_definition():
    source, pos = get_content_and_offset()
    line, fname = env.get().get_location(os.getcwd(), source, pos, 
        vim.current.buffer.name)

    if line:
        if fname and fname != vim.current.buffer.name:
            vim.command(':edit +{} {}'.format(line, fname)) # TODO: escape!
        else:
            vim.current.window.cursor = line, 0
            vim.command('normal! ^')
    else:
        print 'Location not found'

def show_outline():
    outline.show(get_outline(get_content(), vfunc.shiftwidth()))

OUTLINE_REGEX = re.compile(r'(?m)^([ \t]*)(def|class)\s+(\w+)')
def get_outline(source, tw):
    for m in OUTLINE_REGEX.finditer(source):
        ws = m.group(1)
        level = len(ws.replace('\t', ' ' * tw)) // tw
        yield {'level': level, 'name': m.group(3), 'offset': m.start(2)}

def lint(append=False):
    source = get_content()
    errors, warns = _lint(source, vim.current.buffer.name)
    show_lint_result(errors, warns, append)

def lint_all():
    t = time() - 1
    errors, warns = [], []
    for r in get_projects():
        for name, path, root, top, fullpath in get_files(r):
            if name.endswith('.py'):
                if time() - t >= 1:
                    redraw()
                    print fullpath
                    t = time()

                with open(fullpath) as f:
                    source = f.read()

                e, w = _lint(source, fullpath)
                errors += e
                warns += w

    show_lint_result(errors, warns)

def show_lint_result(errors, warns, append=False):
    result = errors + warns
    if not result:
        vim.command('cclose')
        redraw()
        print 'Good job!'
        return

    vfunc.setqflist(errors + warns, 'a' if append else 'r')
    if errors:
        vim.command('copen')

    redraw()
    print '{} error(s) and {} warning(s) found'.format(len(errors), len(warns))

def _lint(source, filename):
    result = env.get().lint(os.getcwd(), source, vim.current.buffer.name)

    errors, warns = [], []
    for (line, col), name, message in result:
        qlist = errors if '(E' in message else warns
        qlist.append({
            'bufnr': '',
            'filename': filename,
            'pattern': '',
            'valid': 1,
            'nr': -1,
            'lnum': line,
            'vcol': 0,
            'col': col + 1,
            'text': message,
            'type': ''
        })

    return errors, warns
                
def show_signature():
    source, pos = get_content_and_offset()
    result = env.get().get_docstring(os.getcwd(), source, pos, vim.current.buffer.name)
    redraw()
    if result:
        print result[0]
    else:
        print 'None'
