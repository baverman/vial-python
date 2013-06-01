from vial import manager
from vial.utils import lfunc

def init():
    manager.on('filetype:python', lfunc('.plugin.python_buffer'))

    manager.register_function('VialPythonOmni(findstart, base)', lfunc('.plugin.omnifunc'))

    manager.register_function('VialPythonExecutableChoice(start, cmdline, pos)',
        lfunc('.plugin.executable_choice'))
    manager.register_command('VialPythonSetExecutable', lfunc('.plugin.set_executable'),
        complete='custom,VialPythonExecutableChoice', nargs=1)
