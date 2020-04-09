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

    if not msg.ask_yn(f'Continue with {as_disp_name}?'):
        print('Bye:)')
        exit(0)

    link = util.get_link(f'{as_name}{as_num}')
    print(f'Link: {msg.underline(link)}')
    if msg.ask_yn('Open in browser?'):
        webbrowser.open_new_tab(link)

    if not os.path.exists('submission'):
        if len(glob.glob('CSC 116*.zip')) == 0:
            return 1
        msg.info('Extracting...')
        g = glob.glob('CSC 116*.zip')
        if len(g) == 1:
            with zipfile.ZipFile(g[0]) as file:
                file.extractall('submission')
    os.chdir('submission')
    return 0


def rename():
    """ Rename all directories to [firstname lastname]. """

    msg.info('Renaming...')
    for entry in os.scandir('.'):
        if '_assignsubmission_file_' not in entry.name:
            return 1

        n = re.split('__', entry.name)[0].split(' ')
        # Projects use [lastname firstname]
        # But exercises and homework use [firstname lastname]
        if not args.project:
            n[0], n[1] = n[1], n[0]
        os.rename(entry.name, ' '.join(n))

    fmt = '[lastname firstname]'
    if not args.project:
        fmt = '[firstname lastname]'
    msg.info(f'Renamed to {fmt}')

    return 0


def javac_all():
    """ Compile all Java files in /src and /test, then copy to /bin. """

    msg.info('Compiling...')

    for student in sorted(os.scandir('.')):
        if not student.is_dir():
            continue
        os.chdir(student)

        msg.name(student.name)
        for file in glob.glob('*.java', recursive=True):
            javac(file)
        os.chdir('..')

    msg.press_continue()


def javac(file, lib='.:../../../../../lib/*'):
    """ Compile a Java file to /bin. """

    msg.info(f'Compiling {msg.underline(file)}...', '')
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
        if msg.ask_retry():
            javac(file)

    return rc


def java(file, arg=''):
    """ Run a compiled Java program. """
    # TODO: Refactor

    msg.info(f'Running {file}...')
    cmd = f'java {arg} {file.replace(".java", "")}'
    if os.system(cmd) != 0:
        msg.fail(f'Failed to run {file} by using:')
        print(f'       {" ".join(cmd.split())}')
        if msg.ask_retry():
            java(file)


def java_all():
    """ Run all Java classes. """
    # TODO: Refactor

    msg.info('Running...')
    for student in os.scandir('.'):
        if not student.is_dir():
            continue


def ts_test():
    """ Run all teaching staff tests. """

    msg.info('Running teaching staff tests...')

    g = glob.glob('../files*')
    if '../files' in g and '../files.zip' not in g:
        msg.fatal('/files or files.zip not found')
    with zipfile.ZipFile('../files.zip') as zf:
        msg.info('Extracting files.zip...')
        zf.extractall('../files')

    for student in sorted(os.scandir('.'), key=lambda s: s.name):
        if not student.is_dir():
            continue
        os.chdir(student.name)
        msg.name(student.name)

        msg.info('Copying TS files...')
        distutils.dir_util.copy_tree('../../files', '.')

        src = util.conf_as('src')
        for f in src:
            msg.info(f'Opening {msg.underline(f)}...')
            sp.Popen(['open', f])

        test = util.conf_as('test')
        for f in test:
            msg.info(f'Opening {msg.underline(f)}...')
            sp.Popen(['open', f])

        total = util.conf_as('src') + util.conf_as('test')

        for item in util.conf_as('order'):
            # Custom run is a dict: {'custom run' : [..., ...]}
            if type(item) is dict:
                _item = next(iter(item))
                msg.info(f'Current grading: {msg.underline(_item)}')
                cmds = item.get(_item)
                run_custom(cmds)
                return

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
                cs = checkstyle(total)
                if cs == 0:
                    msg.info('No checkstyle error found')
                else:
                    msg.warn(f'{cs} checkstyle errors found')

        msg.info('Finish TS testing for current student')
        msg.press_continue()
        input()
        os.chdir('..')


def ts_wce():
    msg.info('Compiling files...')
    msg.info(f'Current grading: {msg.underline("src")}')
    for f in util.conf_as('src'):
        javac(f, '.:*')
        java(f)
    msg.press_continue()
    msg.info(f'Current grading: {msg.underline("test")}')
    for f in util.conf_as('test'):
        javac(f, '.:*')
        java(f)
    msg.press_continue()


def ts_tsbbt():
    msg.info('Compiling TS_BBT...')
    for f in sorted(glob.glob('TS*BB*.java')):
        javac(f, '.:*')
        java(f, '-cp .:* org.junit.runner.JUnitCore')
    msg.press_continue()


def ts_tswbt():
    msg.info('Compiling TS_WBT...')
    ts = glob.glob('TS_*_WB_Runner.java')
    javac(ts[0], '.:*')
    java(ts[0], '-cp .:*')
    msg.press_continue()


def ts_bbt():
    pdf = glob.glob('*.pdf')
    msg.info(f'Opening {pdf[0]}...')
    sp.Popen(['open', pdf[0]])

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
        msg.info(f'Running {msg.underline(f)}...')
        # while sp.call(['javac', '-cp', '.:*', f]) != 0:
        javac(f)
        java(f)
        # sp.call(['java', '-cp', '.:*', 'org.junit.runner.JUnitCore', f])


def checkstyle(files, cs='~/Developer/NCSU/cs-checkstyle/checkstyle'):
    sum = 0
    for f in files:
        cmd = f'{cs} {f} | grep -c ""'
        proc = sp.Popen(cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = proc.communicate()
        out = out.decode('utf-8')
        sum += int(out)
    return sum


def hw(num):
    # TODO: Refactor
    msg.info('Checking homework...')
    for root, dirs, files in os.walk('.'):
        for student in sorted(dirs):
            os.chdir(student)
            msg.info('Opening...')

            if os.system(f'open Homework{num}.pdf &> /dev/null') != 0:
                msg.fail(f'Homework{num}.pdf not found.')
                msg.info('Possible submission file:')
                for root1, dirs1, files1 in os.walk('.'):
                    for i, f in enumerate(files1):
                        msg.warn_index(i + 1, f)
                    skip_index = len(files1) + 1
                    msg.warn_index(skip_index, 'Skip')
                    msg.info('Select a file to open: ', '')
                    item = msg.ask_index(1, skip_index)
                    if item == skip_index:
                        msg.warn('Skipped', '')
                        break
                    while os.system(
                            f'open \'{files1[item - 1]}\' &> /dev/null') != 0:
                        msg.fail(
                            f'No application can'
                            f' open {msg.underline(files1[item - 1])}')
                        for i, f in enumerate(files1):
                            msg.warn_index(i + 1, f)
                        msg.warn_index(skip_index, 'Skip')
                        msg.info('Select a file to open: ', '')
                        item = msg.ask_index(1, skip_index)
                        if item == skip_index:
                            msg.warn('Skipped', '')
                            break
                    msg.info('Opening')
            os.chdir('..')
            input()


def run_custom(cmds):
    for c in cmds:
        while os.system(c) != 0:
            msg.fail(f'Failed to run {msg.underline(c)}')
            if not msg.ask_retry():
                break


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
    parser.add_argument('-j', '--junit',
                        help='compile tests with junit',
                        action='store_true')
    parser.add_argument('-ts', '--tstest',
                        help='teaching staff tests provided',
                        action='store_true')
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

    as_name, as_cat = '', ''
    as_num = 0
    if args.exercise:
        as_cat = 'exercises'
        as_name = 'day'
        as_num = args.exercise.zfill(2)
    elif args.project:
        as_cat = 'projects'
        as_name = 'p'
        as_num = args.project
    elif args.homework:
        as_cat = 'homework'
        as_name = 'hw'
        args.num = args.homework
    else:
        msg.fatal('Invalid arguments. Use -h or --help for usage.')
    as_disp_name = f'{as_cat.capitalize()[:-1]} {as_num}'

    # Path and config
    path_as = os.path.join('content', as_cat, f'{as_name}{as_num}')
    path_as_conf = path_as.replace('content', 'config') + '.yaml'
    util.read_config_glob()
    util.read_config_as(path_as_conf)
    path_cs = util.conf_glob('checkstyle')
    path_lib = util.conf_glob('lib')

    os.chdir(path_as)
    if precheck() != 0:
        msg.fatal('/submission or zip file not found')
    if rename() != 0:
        msg.warn('Already renamed. If not, remove /submission and run again')
        msg.info('Press <return> to continue')
        input()
    if args.homework:
        hw(args.homework)
    if args.tstest:
        ts_test()
    else:
        if not args.nocompile:
            javac_all()
        if not args.norun:
            run_all()
