import argparse
import distutils.dir_util
import glob
import os
import re
import subprocess as sp
import webbrowser
import zipfile

import agsmsg as msg
import agsutil as util


def precheck():
    """ Pre-check the assignment structure before starting grading. """

    if not msg.ask_yn(f'Continue with {msg.underline(asmt_disp_name)}?'):
        print('Bye:)')
        exit(0)

    link = util.get_link(f'{asmt_name}{asmt_num}')
    if msg.ask_yn('Open link in browser?'):
        msg.info(f'Opening {msg.underline(link)}...')
        webbrowser.open_new_tab(link)

    if not os.path.exists('submission'):
        if len(glob.glob('CSC 116*.zip')) == 0:
            return 1
        msg.info('Extracting...')
        g = glob.glob('CSC 116*.zip')
        if len(g) == 1:
            with zipfile.ZipFile(g[0]) as file:
                file.extractall('submission')

    return 0


def rename():
    """ Rename all directories to [firstname lastname]. """

    moodle_sub_specifier = '_assignsubmission_file_'

    msg.info('Renaming...')
    g = glob.glob(f'*{moodle_sub_specifier}')
    if len(g) == 0:
        return -1

    for entry in g:
        print(msg.align_left(msg.name(entry), 80), end='')
        entry_new = ' '.join(re.split('__', entry)[0].split(' '))
        os.rename(entry, entry_new)
        print(f'-> {msg.name(entry_new)}')

    msg.info(f'Renamed to [lastname firstname]')
    return 0


def javac_all():
    """ Compile all Java files in /src and /test, then copy to /bin. """

    msg.info('Compiling...')

    for student in glob.glob('* *'):
        if not student.is_dir():
            continue
        os.chdir(student)

        print(msg.name(student.name))
        files = util.get_conf_asmt('files')
        if files:
            for file in files:
                javac(file)
        else:
            for file in glob.glob('*.java', recursive=True):
                javac(file)

        os.chdir('..')

    msg.press_continue()


def javac(file, lib='.:../../../../../lib/*'):
    """ Compile a Java file to /bin. """

    msg.info(f'Compiling {msg.underline(file)}...', '')
    if not os.path.exists(file):
        print()
        msg.fail(f'{msg.underline(file)} does not exist', '')
        input()
        return -1

    # src
    cmd = f'javac {file}'
    # test
    if file.startswith('TS_') or file.endswith('Test.java'):
        if args.junit or args.tstest:
            cmd = f'javac -cp {lib} {file}'

    proc = sp.Popen(cmd, shell=True,
                    stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = proc.communicate()
    rc = proc.wait()
    out = out.decode(encoding='utf-8')
    err = err.decode(encoding='utf-8')
    if not args.nostacktrace:
        if len(out) > 0:
            print()
            msg.info(f'Output:\n{out}')
        if len(err) > 0:
            print()
            msg.fail(f'Error:\n{err}')

    if rc != 0:
        print()
        msg.fail(f'Failed to compile {msg.underline(file)} by using:')
        print(f'       {cmd}')
        sp.Popen([default_open, file])
        if msg.ask_retry():
            javac(file)
    else:
        print('done')
    return rc


def java(file, arg='', arg2=''):
    """ Run a compiled Java program. """
    # TODO: Refactor

    msg.info(f'Running {file}...')
    cmd = f'java -cp ".:*" {arg} {file.replace(".java", "")} {arg2}'
    if os.system(cmd) != 0:
        msg.fail(f'Failed to run by {msg.underline(" ".join(cmd.split()))}')
        if msg.ask_retry():
            java(file)


def java_all():
    """ Run all Java classes. """

    msg.info('Running...')
    for student in sorted(os.scandir('.'), key=lambda s: s.name):
        if not student.is_dir():
            continue

        print(msg.name(student.name))
        os.chdir(student.name)

        cmds = util.get_conf_asmt('custom run')
        files = util.get_conf_asmt('files')

        if cmds:
            run_custom(cmds)
        elif files:
            for f in files:
                java(f)
        else:
            for f in glob.glob('*.java'):
                java(f)

        os.chdir('..')


def ts_test():
    """ Run all teaching staff tests. """

    msg.info('Running teaching staff tests...')
    with zipfile.ZipFile(args.tstest) as zf:
        msg.info(f'Extracting {args.tstest}...')
        zf.extractall('ts')

    ts_path = os.path.abspath('ts')
    os.chdir('submission')

    for student in sorted(glob.glob('* *')):
        os.chdir(student)
        print(msg.name(student))

        msg.info('Copying TS files...')
        distutils.dir_util.copy_tree(ts_path, '.')

        src = util.get_conf_asmt('src')
        for f in src:
            msg.info(f'Opening {msg.underline(f)}...')
            sp.Popen([default_open, f])

        test = util.get_conf_asmt('test')
        for f in test:
            msg.info(f'Opening {msg.underline(f)}...')
            sp.Popen([default_open, f])

        for item in util.get_conf_asmt('order'):
            # Custom run is a dict: {'custom run' : [..., ...]}
            if type(item) is dict:
                _item = next(iter(item))
                msg.info(f'Current grading: {msg.underline(_item)}')
                cmds = item.get(_item)
                run_custom(cmds)
                continue

            _item = item.lower()
            msg.info(f'Current grading: {msg.underline(item)}')
            if _item == 'wce':
                ts_wce()
            elif _item == 'tsbbt':
                ts_tsbbt()
            elif _item == 'tswbt':
                ts_tswbt()
            elif _item == 'bbt':
                ts_bbt()
            elif _item == 'wbt':
                ts_wbt(test)
            elif _item == 'style' or _item == 'checkstyle':
                cs = checkstyle(src, test)
                if cs == 0:
                    msg.info('No checkstyle error found')
                else:
                    msg.warn(f'{cs} checkstyle errors found')

        msg.info('Finish TS testing for current student')
        msg.press_continue()
        os.chdir('..')


def ts_wce():
    msg.info('Compiling files...')
    msg.info(f'Current grading: {msg.underline("src")}')
    arg2 = args.argument if args.argument else ''
    for f in util.get_conf_asmt('src'):
        javac(f, '.:*')
        java(f, arg2=arg2)
    msg.press_continue()
    msg.info(f'Current grading: {msg.underline("test")}')
    for f in util.get_conf_asmt('test'):
        javac(f, '.:*')
        java(f, arg='org.junit.runner.JUnitCore')
    msg.press_continue()


def ts_tsbbt():
    msg.info('Compiling TS_BBT...')
    for f in sorted(glob.glob('TS_*_BB_Test.java')):
        javac(f, '.:*')
        java(f, arg='org.junit.runner.JUnitCore')
    msg.press_continue()


def ts_tswbt():
    msg.info('Compiling TS_WBT...')
    ts = glob.glob('TS_*_WB_Runner.java')
    javac(ts[0], '.:*')
    java(ts[0])
    msg.press_continue()


def ts_bbt():
    pdf = glob.glob('*.pdf')
    if len(pdf) != 1:
        msg.fail('BBTP pdf file not found')
        input()
        return

    msg.info(f'Opening {pdf[0]}...')
    sp.Popen([util.get_conf_glob('open'), pdf[0]])

    cmd = None
    while msg.ask_yn('Continue running?'):
        msg.info(f'Current command: {msg.underline(cmd)}')
        if cmd is None:
            msg.info('Enter a command to execute: ')
            cmd = input()
        else:
            if msg.ask_yn('Change the current command?'):
                cmd = input()
            else:
                msg.info('No change')
        msg.info(f'Running {cmd}...')
        os.system(cmd)


def ts_wbt(test):
    for f in test:
        javac(f)
        java(f, 'org.junit.runner.JUnitCore')


def checkstyle(src, test, cs='~/cs-checkstyle/checkstyle'):
    total = 0
    for f in src:
        msg.textbar(f)
        cmd = f'{cs} {f} | grep -c ""'
        proc = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        num = int(proc.stdout) - 4
        total += num
        print(msg.align_right(num, 3))
    # Ignore magic numbers for test files
    for f in test:
        msg.textbar(f)
        cmd = f'{cs} {f} | grep -v "is a magic number" -c'
        proc = sp.run(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        num = int(proc.stdout) - 4
        total += num
        print(msg.align_right(num, 3))
    return total


def checkstyle_all():
    for student in sorted(os.scandir('.'), key=lambda s: s.name):
        if not student.is_dir():
            continue
        os.chdir(student.name)
        print(msg.name(student.name, swap=True))

        src = util.get_conf_asmt('src')
        test = util.get_conf_asmt('test')
        total = checkstyle(src, test)
        print('-' * 30)
        msg.textbar('Total')
        print(msg.align_right(total, 3))

        print()
        os.chdir('..')


def hw():
    msg.info('Checking homework...')
    folders = glob.glob('* *')
    for f in folders:
        print(msg.name(f))
        os.chdir(f)

        files = glob.glob('*.*')
        num = len(files)
        if num == 0:
            msg.fail('No submission')
        elif num == 1:
            pdf = files[0]
            msg.info(f'Opening {msg.underline(pdf)}...')
            sp.Popen(f'{default_open} \"{pdf}\"', shell=True)
        else:
            msg.warn(f'Multiple files found (total {num}):')
            msg.index_list(files)
            print('Select a file to open: ', end='')
            i = msg.ask_index(0, num)
            if 0 < i < num:
                pdf = files[i]
                msg.info(f'Opening {msg.underline(pdf)}...')
                sp.Popen(f'{default_open} \"{pdf}\"', shell=True)

        input()
        os.chdir('..')


def run_custom(cmds):
    for c in cmds:
        msg.info(f'Running {msg.underline(c)}')
        while sp.call(c, shell=True) != 0:
            print()
            msg.fail(f'Failed to run {msg.underline(c)}')
            if not msg.ask_retry():
                print()
                break
        # msg.press_continue()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='The automatic grading script for CSC 116. '
                        'GitHub Repository: '
                        'https://github.com/apo5698/ags-cli')
    parser.add_argument('-e', '--exercise', help='grade an exercise')
    parser.add_argument('-p', '--project', help='grade a project')
    parser.add_argument('-hw', '--homework', help='grade a homework')

    parser.add_argument('-i', '--init',
                        nargs='?',
                        const=' ',
                        help='initialize system')
    parser.add_argument('-r', '--reset',
                        help='reset current assignment',
                        action='store_true')
    parser.add_argument('-v', '--version',
                        help='display the current version',
                        action='store_true')
    parser.add_argument('-c', '--checkstyle',
                        help='run checkstyle',
                        action='store_true')
    parser.add_argument('-j', '--junit',
                        help='compile tests with junit',
                        action='store_true')
    parser.add_argument('-t', '--tstest',
                        help='teaching staff tests provided')
    parser.add_argument('-a', '--argument',
                        help='add argument for running src')
    parser.add_argument('-nc', '--nocompile',
                        help='do not compile',
                        action='store_true')
    parser.add_argument('-nr', '--norun',
                        help='do not run',
                        action='store_true')
    parser.add_argument('-ns', '--nostacktrace',
                        help='do not print stacktrace',
                        action='store_true')

    args = parser.parse_args()

    if args.version:
        print(open('./VERSION').read())
        exit(0)

    msg.info('Starting service...')
    if args.init:
        force = True if args.init == 'f' else False
        util.init(force)
        exit()

    asmt_name, asmt_cat, asmt_num = None, None, None
    if args.exercise:
        asmt_cat = 'exercise'
        asmt_name = 'day'
        asmt_num = args.exercise.zfill(2)
    elif args.project:
        asmt_cat = 'project'
        asmt_name = 'p'
        asmt_num = args.project
    elif args.homework:
        asmt_cat = 'homework'
        asmt_name = 'hw'
        asmt_num = args.homework
    else:
        msg.fatal('Invalid arguments. Use -h or --help for usage.')
    asmt_disp_name = f'{asmt_cat.capitalize()} {asmt_num}'

    # Path and config
    path_asmt = os.path.join('content', asmt_cat, f'{asmt_name}{asmt_num}')
    if args.exercise:
        util.read_config_asmt(f'{path_asmt.replace("content", "config")}.yaml')
    elif args.project:
        util.read_config_asmt(
                f'{path_asmt.replace("content", "config")}_'
                f'{util.current_semester()}.yaml')

    util.read_config_glob()
    path_cs = util.get_conf_glob('checkstyle')
    path_lib = util.get_conf_glob('lib')
    default_open = util.get_conf_glob('open')

    os.chdir(path_asmt)
    if precheck() != 0:
        msg.fatal('zip file or /submission not found')
    if rename() != 0:
        msg.warn('Already renamed. If not, remove /submission and run again')
        msg.press_continue()
    if args.homework:
        hw()
    elif args.tstest:
        ts_test()
    else:
        if args.checkstyle:
            checkstyle_all()
        if not args.nocompile:
            javac_all()
        if not args.norun:
            java_all()
