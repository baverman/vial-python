import vial
from vial.utils import lfunc

def init():
    vial.event.on('filetype:python', lfunc('.plugin.python_buffer'))

    vial.register_function('VialPythonOmni(findstart, base)', lfunc('.plugin.omnifunc'))

    vial.register_function('VialPythonExecutableChoice(start, cmdline, pos)',
        lfunc('.plugin.executable_choice'))
    vial.register_command('VialPythonSetExecutable', lfunc('.plugin.set_executable'),
        complete='custom,VialPythonExecutableChoice', nargs=1)

    vial.register_command('VialPythonGotoDefinition', lfunc('.plugin.goto_definition'))
    vial.register_command('VialPythonOutline', lfunc('.plugin.show_outline'))
    vial.register_command('VialPythonShowSignature', lfunc('.plugin.show_signature'))

    vial.register_command('VialPythonLint', lambda: lfunc('.plugin.lint')(False))
    vial.register_command('VialPythonLintAdd', lambda: lfunc('.plugin.lint')(True))
    vial.register_command('VialPythonLintAll', lfunc('.plugin.lint_all'))
