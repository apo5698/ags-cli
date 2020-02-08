import os
import re
import sys
import webbrowser

##################################################
#            DO NOT CHANGE CODE BELOW            #
##################################################


class color:
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94

    def print(color, str):
        return f'\33[{color}m{str}\33[0m'


is_exercise = True
link_prefix = 'https://www.csc.ncsu.edu/courses/csc116-common/CSC116/Balik/Exercises/'
links = {'day01': f'{link_prefix}HelloWorld.pdf',
         'day02': f'{link_prefix}IntroToJavaProceduralComposition.pdf',
         'day03': f'{link_prefix}BMICalculator.pdf',
         'day04': f'{link_prefix}forLoops.pdf',
         'day05': f'{link_prefix}NestedLoopsAndMethods.pdf',
         'day06': f'{link_prefix}UsingObjects.pdf',
         'day07': f'{link_prefix}Graphics.pdf',
         'day08': f'{link_prefix}GradeCalculatorProgram.pdf',
         'day09': f'{link_prefix}TextProcessing.pdf',
         'day11': f'{link_prefix}SoftwareTesting.pdf',
         'day13': f'{link_prefix}FunWithFiles.pdf',
         'day15': f'{link_prefix}WorkingWithOutputFiles.pdf',
         'day16': f'{link_prefix}ArraysAndStatistics.pdf',
         'day17': f'{link_prefix}ArrayParametersAndReturnValues.pdf',
         'day18': f'{link_prefix}2DArraysAndClasses.pdf',
         'day19': f'{link_prefix}WeatherInfo.pdf',
         'day21': f'{link_prefix}InteractingClasses.pdf',
         'day22': f'{link_prefix}CSC116Review.pdf',
         'day23': f'{link_prefix}Project6.pdf',
         'day24': f'{link_prefix}ComprehensiveExercisePart1.html',
         'day25': f'{link_prefix}ComprehensiveExercisePart2.html',
         'day26': f'{link_prefix}ComprehensiveExercisePart3.html',
         'day27': f'{link_prefix}ComprehensiveExercisePresentationDemo.html'
         }


def autograde(dirname, src='.', bin='.'):
    """ This method will simply do everything for you.\n
    Common usages:\n
    \tautograde('day01'): daily exercises\n
    \tautograde('p1', 'src', 'bin'): projects
    """

    name_split = re.findall('\d+|\D+', dirname)
    if name_split[0] == 'd' or name_split[0] == 'day':
        os.chdir('exercises')
        name_split[0] = 'day'
        name_split[1] = name_split[1].zfill(2)
    if name_split[0] == 'p' or name_split[0] == 'project':
        os.chdir('projects')
        name_split[0] = 'p'
        name_split[1] = name_split[1].strip("0")
        global is_exercise
        is_exercise = False
    dirname = name_split[0] + name_split[1]
    display_name = "Day " if is_exercise else "Project "
    display_name = display_name + name_split[1].strip("0")

    if os.path.exists(dirname):
        os.chdir(dirname)
        success(f'{display_name} found')
        if is_exercise:
            state(links.get(dirname))
            webbrowser.open(links.get(dirname), new=2)
    else:
        fail(f'{display_name} not found')
        exit(1)

    precheck()
    rename_dir('.')
    compile_all(src, bin, '.')
    run_all(bin, '.')


def precheck():
    """ Do some prechecks before starting grading.
    Unzip the view.zip directly to /view.
    Do not change the directory name.
    """

    state('Current directory:')
    print(os.getcwd())

    state('Continue? [Y/n]')
    option = input().lower()
    while option != 'y' and option != 'n':
        fail(f'Invalid option: {option}')
        option = input().lower()
    if option == 'n':
        state('Bye~')
        exit(0)

    if not os.path.exists('view'):
        fail('/view not found')
        exit(1)

    success('/view found')
    os.chdir('view')

    for root, dirs, files in os.walk('.'):
        if len(dirs) == 0:
            fail('/view is empty')
            exit(1)
        else:
            success('/view not empty')
            break

    success('Precheck done\n')


def rename_dir(dirname='.'):
    """ Rename all directories to [firstname lastname]. """

    state('Renaming...')

    for root, dirs, files in os.walk(dirname):
        for dir in dirs:
            # Already parsed
            if '__' not in dir:
                warn(
                    'Already renamed. If not, please remove /view and unzip view.zip again')
                input()
                return

            id = re.split('__', dir)[0].split(' ')  # double underscores
            # Exercises use [firstname lastname]
            # Projects use [lastname firstname]
            if is_exercise:
                id[0], id[1] = id[1], id[0]
            name = ' '.join(id)
            os.rename(dir, name)

    if is_exercise:
        success('Done [firstname lastname]')
    else:
        success('Done [lastname firstname]')
    input()


def compile(filename, src='.', bin='.'):
    """ Compile a Java file in current directory.\n
    If not specified, all Java files will be compiled in current directory by default.
    """

    path = os.path.join(src, filename)
    state(f'Compiling {path} to {bin}')

    if os.system(f'javac -d \"{bin}\" \"{path}\"') == 0:
        success('Done')
    else:
        fail('Compile failed. Try again? [Y/n]')
        option = input().lower()
        while option != 'y' and option != 'n':
            fail(f'Invalid option: {option}')
            option = input().lower()
        if option == 'n':
            warn('Skipped')
            return

        compile(filename, src, bin)


def compile_all(src='.', bin='.', dirname='.'):
    """ Compile all Java files in every subdirectory.\n
    src and bin are '.' (current directory) by default (for daily exercises).\n
    Use compile_all('src', 'bin') to grade a project.
    """
    state('Compiling...')

    for root, dirs, files in os.walk(dirname):
        for dir in sorted(dirs):
            print_name(dir)
            student = os.path.join(dirname, dir)
            _src = os.path.join(student, src)
            _bin = os.path.join(student, bin)
            for root, dirs, files in os.walk(student):
                for file in files:
                    if file.endswith('.java'):
                        compile(file, _src, _bin)
            print()

    state('Compiling done')
    input()


def run(classname, bin='.'):
    """ Run a compiled Java program.\n
    If not specified, the Java file in current directory will be executed by default.
    """

    path = os.path.join(bin, classname)
    _classname = classname.replace('.class', '')
    state(f"Running {_classname}.java")
    if not os.path.exists(path):
        fail(f'{classname} not found')

    if os.system(f'java -cp \"{bin}\" \"{_classname}\"') == 0:
        success('Done')
    else:
        fail('Run failed')

    input()


def run_all(bin='.', dirname='.'):
    """ Run all Java files in every subdirectory.\n
    bin is '.' (current directory) by default (for daily exercises).\n
    Use run_all('bin') to grade a project.
    """
    state('Running...')

    for root, dirs, files in os.walk(dirname):
        for dir in sorted(dirs):
            print_name(dir)
            student = os.path.join(dirname, dir)
            _bin = os.path.join(student, bin)
            for root, dirs, files in os.walk(student):
                for file in sorted(files):
                    if file.endswith('.class'):
                        run(file, _bin)
            print()

    state('Running done')
    input()


def state(str):
    print(f'--> {str}')


def success(str='Done'):
    print(color.print(color.GREEN, f'[o] {str}'))


def fail(str='Failed'):
    print(color.print(color.RED, f'[x] {str}'))


def warn(str='Warning'):
    print(color.print(color.YELLOW, f'[!] {str}'))


def print_name(str):
    print(color.print(color.BLUE, str))


##################################################
#            DO NOT CHANGE CODE ABOVE            #
##################################################


if __name__ == '__main__':
    if len(sys.argv) != 2:
        fail('Usage: python autograde.py <assignment>')
        print('           python3 autograde.py <assignment>')
        exit(1)

    autograde(sys.argv[1])
