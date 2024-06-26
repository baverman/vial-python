import re
import sys
import os.path

from time import time

from vial import vfunc, vim, outline
from vial.compat import sstr
from vial.helpers import echoerr
from vial.utils import get_dict_var, get_content_and_offset, get_content, \
    redraw, get_projects, mark
from vial.fsearch import get_files

from . import env

last_result = None


def omnifunc(findstart, base):
    global last_result
    if findstart in (0, b'0', '0'):
        return [r for r in last_result[1] if r.startswith(base)]
    else:
        source = get_content()
        pos = vim.current.window.cursor
        try:
            m, _ = last_result = env.get().assist(source, pos,
                                                  vim.current.buffer.name)
        except Exception as e:
            print(e.message, file=sys.stderr)
            m = None

        if m is None:
            return -3
        else:
            return pos[1] - len(m)


def executable_choice(start, cmdline, pos):
    executables = set(('default', 'python2', 'python3'))\
        .union(env.get_virtualenvwrapper_executables())\
        .union(get_dict_var('vial_python_executables'))

    return '\n'.join(sorted(executables))


def set_executable(name):
    vim.vars['vial_python_executable'] = name


def goto_definition():
    source = get_content()
    pos = vim.current.window.cursor
    locs = env.get().location(source, pos, vim.current.buffer.name)

    if locs:
        mark()
        last = locs[-1]
        if isinstance(last, dict):
            head = locs[:-1]
            tail = [last]
        else:
            tail = last
            last = tail[0]
            head = locs[:-1]

        locs = head + tail
        if len(locs) > 1:
            llist = [{
                'bufnr': '',
                'filename': loc['file'],
                'pattern': '',
                'valid': 1,
                'nr': -1,
                'lnum': loc['loc'][0],
                'vcol': 0,
                'col': loc['loc'][1] + 1,
            } for loc in locs]
            vfunc.setloclist(0, llist, ' ')
            vim.command(':ll {}'.format(len(head) + 1))
            redraw()
            if len(tail) > 1:
                print('Multiple locations')
            else:
                print('Chained locations')
        else:
            fname = last['file']
            dpos = last['loc']
            if fname and fname != vim.current.buffer.name:
                vim.command(':edit {}'.format(sstr(vfunc.fnameescape(fname))))
                vim.current.window.cursor = dpos
            else:
                vim.current.window.cursor = dpos
    else:
        redraw()
        print('Location not found')


def show_outline():
    outline.show(get_outline(get_content(), vfunc.shiftwidth()))


OUTLINE_REGEX = re.compile(r'(?m)^([ \t]*)(async\s+def|def|class|if|elif|else|try|except|with)\s+(\w+)')
DEAD_NODES = set(('if', 'elif', 'else', 'elif', 'try', 'except', 'with'))
def get_outline(source, tw):
    for m in OUTLINE_REGEX.finditer(source):
        ws = m.group(1)
        level = len(ws.replace('\t', ' ' * tw)) // tw

        node = {'level': level, 'name': m.group(3), 'offset': m.start(2)}

        if m.group(2) in DEAD_NODES:
            node['dead'] = True

        yield node


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
                    print(fullpath)
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
        print('Good job!')
        return

    vfunc.setqflist(errors + warns, 'a' if append else ' ')
    if errors:
        vim.command('copen')

    redraw()
    print('{} error(s) and {} warning(s) found'.format(len(errors), len(warns)))


def _lint_result_key(item):
    return item['lnum'], item['col']


def _lint(source, filename):
    result = env.get().lint(source, vim.current.buffer.name)

    errors, warns = [], []
    for etype, message, line, col in result:
        qlist = errors if etype[0] == 'E' else warns
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
            'type': etype
        })

    errors.sort(key=_lint_result_key)
    warns.sort(key=_lint_result_key)
    return errors, warns


def show_signature():
    source, pos = get_content_and_offset()
    result = env.get().get_docstring(source, pos, vim.current.buffer.name)
    redraw()
    if result:
        print(result[0])
    else:
        print('None')


def open_module_choice(start, cmdline, pos):
    syspath = env.get().eval('import sys\nreturn sys.path')
    syspath = env.get_sources() + syspath
    modules = set()

    prefix = start.split('.')[:-1]
    dprefix = '.'.join(prefix)
    if dprefix:
        dprefix += '.'

    for p in syspath:
        if prefix:
            p = os.path.join(p, *prefix)

        if p.endswith('.zip'):
            continue

        try:
            dlist = os.listdir(p)
        except OSError:
            continue

        for name in dlist:
            if name.endswith('.py'):
                modules.add(dprefix + name[:-3])
            elif os.path.exists(os.path.join(p, name, '__init__.py')):
                modules.add(dprefix + name)

    return '\n'.join(sorted(modules))


def open_module(name):
    syspath = env.get().eval('import sys\nreturn sys.path')
    syspath = env.get_sources() + syspath

    mname = name.split('.')
    pkgname = mname[:] + ['__init__.py']
    mname[-1] += '.py'

    foundpath = None
    for p in syspath:
        n = os.path.join(p, *mname)
        if os.path.exists(n):
            foundpath = n
            break

        n = os.path.join(p, *pkgname)
        if os.path.exists(n):
            foundpath = n
            break

    if foundpath:
        mark()
        vim.command('edit {}'.format(foundpath))
    else:
        print("Can't find {}".format(name), file=sys.stderr)


def create_module(name):
    parts = name.split('.')
    pkg = parts[:-1]
    module = parts[-1]

    root = env.get_sources()[0]
    for r in pkg:
        path = os.path.join(root, r)
        if not os.path.exists(path):
            os.mkdir(path)

        init = os.path.join(path, '__init__.py')
        if not os.path.exists(init):
            with open(init, 'w') as f:
                f.write('')
        root = path

    mark()
    vim.command('edit {}'.format(os.path.join(root, module + '.py')))
