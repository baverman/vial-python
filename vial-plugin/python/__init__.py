import vial
from vial import lfunc

def init():
    vial.register_function('VialPythonOmni(findstart, base)', '.plugin.omnifunc')

    vial.register_function('<SID>VialPythonExecutableChoice(start, cmdline, pos)',
        '.plugin.executable_choice')
    vial.register_command('VialPythonSetExecutable', '.plugin.set_executable',
        complete='custom,<SID>VialPythonExecutableChoice', nargs=1)

    vial.register_command('VialPythonGotoDefinition', '.plugin.goto_definition')
    vial.register_command('VialPythonOutline', '.plugin.show_outline')
    vial.register_command('VialPythonShowSignature', '.plugin.show_signature')

    vial.register_command('VialPythonLint', lambda: lfunc('.plugin.lint')(False))
    vial.register_command('VialPythonLintAdd', lambda: lfunc('.plugin.lint')(True))
    vial.register_command('VialPythonLintAll', '.plugin.lint_all')

    vial.register_function('<SID>VialPythonOpenModuleChoice(start, cmdline, pos)',
        '.plugin.open_module_choice')
    vial.register_command('VialPythonOpenModule', '.plugin.open_module',
        complete='custom,<SID>VialPythonOpenModuleChoice', nargs=1)
