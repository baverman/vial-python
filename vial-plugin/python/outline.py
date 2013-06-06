import re

from vial import vim, vfunc
from vial.widgets import SearchDialog, ListFormatter, ListView
from vial.utils import get_content, redraw, focus_window

dialog = None
def show():
    global dialog
    if not dialog:
        dialog = Outline()

    dialog.open()


class HoldIt(object):
    def __init__(self, it):
        self.it = it
        self._hold = []

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._hold:
            return self._hold.pop(0)
        else:
            return next(self.it)

    def hold(self, value):
        self._hold.append(value)


OUTLINE_REGEX = re.compile(r'(?m)^([ \t]*)(def|class)\s+(\w+)')
def get_outline(source, tw):
    result = []
    it = HoldIt(OUTLINE_REGEX.finditer(source))

    def push_childs(plevel, parent):
        for m in it:
            ws = m.group(1)
            level = len(ws.replace('\t', ' ' * tw)) // tw
            if level == plevel:
                result.append((level, m.group(2), parent + (m.group(3),), m.start(2)))
            elif level > plevel:
                it.hold(m)
                push_childs(level, result[-1][2])
            else:
                it.hold(m)
                return

    push_childs(0, ())
    return result

class Outline(SearchDialog):
    def __init__(self):
        self.items = []
        view = ListView(self.items, ListFormatter(1,0, 2,1))
        SearchDialog.__init__(self, '__python_outline__', view)

    def fill(self):
        self.list_view.clear()
        for l, t, name, start in self.outline:
            self.items.append((name, '  ' * l + name[-1], '', start))

        self.list_view.render()
        self.loop.refresh()

    def on_select(self, item, cursor):
        focus_window(self.last_window)
        line = vfunc.byte2line(item[-1] + 1)
        vim.command('normal! {}Gzz'.format(line))

    def on_cancel(self):
        focus_window(self.last_window)

    def open(self):
        self.last_window = vfunc.winnr()

        source = get_content()
        self.outline = get_outline(source, vfunc.shiftwidth())

        self.show('')
        self.fill()
        self.loop.enter()

    def search(self, prompt):
        self.list_view.clear()
        matchers =[
            lambda r: r.startswith(prompt),
            lambda r: prompt in r,
            lambda r: r.lower().startswith(prompt),
            lambda r: prompt in r.lower()
        ]

        already_matched = {}
        for m in matchers:
            for l, t, name, start in self.outline:
                n = name[-1]
                p = name[:-1]
                if start not in already_matched and m(n):
                    already_matched[start] = True
                    self.items.append((name, n, ' / '.join(p), start))

        self.list_view.render()
        self.loop.refresh()

    def on_prompt_changed(self, prompt):
        if prompt:
            self.search(prompt)
        else:
            self.fill()

