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

OUTLINE_REGEX = re.compile(r'(?m)^([ \t]*)(def|class)\s+(\w+)')
def get_outline(source, tw):
    for m in OUTLINE_REGEX.finditer(source):
        ws = m.group(1)
        level = len(ws.replace('\t', ' ' * tw)) // tw
        yield level, m.group(2), m.group(3), m.start(2)

class Outline(SearchDialog):
    def __init__(self):
        self.items = []
        view = ListView(self.items, ListFormatter(1,0, 2,1))
        SearchDialog.__init__(self, '__python_outline__', view)

    def fill(self):
        self.list_view.clear()
        for l, t, name, start in self.outline:
            self.items.append((name, '  ' * l + name, '', start))

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
        self.outline = list(get_outline(source, vfunc.shiftwidth()))

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
                if (start, name) not in already_matched and m(name):
                    already_matched[(start, name)] = True
                    self.items.append((name, name, '', start))

        self.list_view.render()
        self.loop.refresh()

    def on_prompt_changed(self, prompt):
        if prompt:
            self.search(prompt)
        else:
            self.fill()

