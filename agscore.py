import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

import agsmsg as msg
import agsutil as util


# Constants
ASGMT_EX = 0
ASGMT_PR = 1
ASGMT_HW = 2


def precheck():
    """ Pre-check the assignment structure before starting grading. """

    msg.info(f"Current assignment: {msg.underline(asgmt_path)}")
    msg.info(f"Link: {util.get_link(asgmt_type, asgmt_num)}")

    option = msg.prompt_yn("Continue?")
    if option == False:
        print("🌞 Bye~")
        exit(0)

    if not os.path.exists("view"):
        if os.path.isfile("view.zip"):
            if os.system("unzip -q -o view.zip -d view") == 0:
                msg.info("Unzip done")
        else:
            msg.fatal("/view or view.zip not found")

    os.chdir("view")
    for root, dirs, files in os.walk("."):
        if len(dirs) == 0:
            msg.fatal("/view is empty")
            continue
        break

    msg.info("Precheck done")


def rename():
    """ Rename all directories to [firstname lastname]. """

    msg.info("Renaming...")

    for entry in os.scandir("."):
        if "_assignsubmission_file_" not in entry.name:
            msg.warn("Already renamed. "
                     "If not, remove /view and unzip view.zip again", "")
            input()
            return

        temp = re.split("__", entry.name)[0].split(" ")

        # Exercises use [firstname lastname]
        # Projects use [lastname firstname]
        if asgmt_type != 1:
            temp[0], temp[1] = temp[1], temp[0]
        temp = " ".join(temp)
        os.rename(entry.name, temp)

    if asgmt_type == 1:
        msg.info("Renamed to [lastname firstname]")
    else:
        msg.info("Renamed to [firstname lastname]")

    input()


def javac(file):
    """ Compile a Java file in current directory. If not specified,
    all Java files will be compiled to current directory by default.

    """

    msg.info(f"Compiling {msg.underline(file)}...")

    redirect = " &> /dev/null" if not util.get_setting("stacktrace") else ""
    if os.system(f"javac -d bin -cp bin \"{file}\"{redirect}") != 0:
        msg.fail("Compile failed")
        option = msg.prompt_yn("Compile again?")
        if option == False:
            msg.warn("Skipped")
            return
        javac(file, True)


def javac_all():
    """ Compile all Java files in /src and copy to /bin. """

    msg.info("Compiling...")

    for entry in os.scandir("."):
        if not entry.is_dir():
            continue
        os.chdir(entry)

        msg.name(entry.name)
        if not os.path.exists("src"):
            os.mkdir("src")
        if not os.path.exists("bin"):
            os.mkdir("bin")

        if asgmt_type == 1 and asgmt_num == 2:
            msg.info(f"Compiling {msg.underline('DrawingPanel.java')}...")
            dp = os.path.join(lib_path, "DrawingPanel.java")
            os.system(f"javac -d bin -cp bin \"{dp}\"")

        sources = glob.glob(os.path.join(os.getcwd(), "*.java"))
        for file in sources:
            shutil.move(file, "src")
        for _entry in sorted(os.scandir("src"), key=lambda f: f.name):
            if _entry.is_file() and _entry.name.endswith(".java"):
                javac(os.path.join("src", _entry.name))

        os.chdir("..")

    msg.info("Compiling done")
    input()


def run(classname, grep="", grep_option=""):
    """ Run a compiled Java program. If not specified, the Java file in
    current directory will be executed by default.

    """

    binpath = os.path.join("bin", classname)
    name = classname.replace(".class", "")
    srcpath = os.path.join("src", f"{name}.java")

    msg.info(f"Running {name}.java...")
    if not os.path.exists(binpath):
        msg.fail(f"{classname} not found")

    os.system(f"open {srcpath}")
    if os.system(f"java -cp bin \"{name}\"") == 0:
        msg.info("Done")
        msg.info("Running CheckStyle...")
        err = checkstyle(srcpath, grep, grep_option)
        if err == 0:
            msg.info("No CheckStyle error found")
        else:
            msg.warn(f"{msg.bold(err)} checkstyle errors")
    else:
        msg.fail("Run failed")

    input()


def run_all():
    """ Run all Java classes in /bin. """

    msg.info("Running...")

    for entry in os.scandir("."):
        if not entry.is_dir():
            continue
        os.chdir(entry)

        msg.name(entry.name)
        for _entry in sorted(os.scandir("bin"), key=lambda f: f.name, reverse=True):
            _name = _entry.name
            if _entry.is_file() and not _name.startswith("DrawingPanel") and not _name.startswith("TS_") and _name.endswith(".class"):
                run(_name)
        os.chdir("..")

    msg.info("Running done")
    input()


def checkstyle(file, grep="", grep_option=""):
    cmd = f"var=$({cs_path} {file} | grep {grep_option} '{grep}' -c) ; ((var-=4)) ; echo \"$var\""
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out.decode("ascii").strip()


def ts_bbt(java, *files):
    java = java.replace(".class", "")
    for ts in files:
        msg.info(f"Running {java} with {msg.underline(ts)}...")
        path = os.path.join(ts_path, ts)
        os.system(f"java -cp bin {java} < \"{path}\"")
        # input()


def ts_wbt(*files):
    for ts in files:
        msg.info(f"Compiling {msg.underline(ts)}...")
        path = os.path.join(ts_path, ts)
        if os.system(f"javac -d bin -cp bin \"{path}\"") != 0:
            msg.fail(f"Compiling failed")
        msg.info(f"Running {msg.underline(ts)}...")
        os.system(f"java -cp bin \"{ts.replace('.java', '')}\"")
        # input()


def hw(num):
    msg.info("Checking homework...")
    for root, dirs, files in os.walk("."):
        for student in sorted(dirs):
            msg.temp(student)
            os.chdir(student)
            msg.info("Opening...")

            if os.system(f"open Homework{num}.pdf &> /dev/null") != 0:
                msg.fail(f"Homework{num}.pdf not found.")
                msg.info("Possible submission file:")
                for root1, dirs1, files1 in os.walk("."):
                    for i, f in enumerate(files1):
                        msg.warn_index(i + 1, f)
                    skip_index = len(files1) + 1
                    msg.warn_index(skip_index, "Skip")
                    msg.info("Select a file to open: ", "")
                    item = msg.prompt_index(1, skip_index)
                    if item == skip_index:
                        msg.warn("Skipped", "")
                        break
                    while os.system(f"open \"{files1[item - 1]}\" &> /dev/null") != 0:
                        msg.fail(
                            f"No application can open {msg.underline(files1[item - 1])}")
                        for i, f in enumerate(files1):
                            msg.warn_index(i + 1, f)
                        msg.warn_index(skip_index, "Skip")
                        msg.info("Select a file to open: ", "")
                        item = msg.prompt_index(1, skip_index)
                        if item == skip_index:
                            msg.warn("Skipped", "")
                            break
                    msg.info("Opening")
            else:
                msg.info("Done")
            os.chdir("..")
            input()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="The automatic grading script for CSC 116. "
                    "GitHub Repository: https://github.com/apo5698/AGS")
    parser.add_argument("-e", "--exercise", help="grading an exercise")
    parser.add_argument("-p", "--project", help="grading a project")
    parser.add_argument("-hw", "--homework", help="grading a homework")
    parser.add_argument(
        "-v", "--version", help="display the current version", action='store_true')
    args = parser.parse_args()

    asgmt_path = "."

    # 0 is exercise, 1 is project, 2 is homework
    asgmt_type = ASGMT_EX
    asgmt_num = 0

    if args.version:
        print(open("./VERSION").read())
        exit(0)

    if args.exercise:
        asgmt_path = os.path.join("exercises", f"day{args.exercise.zfill(2)}")
        asgmt_num = int(args.exercise.zfill(2))
    elif args.project:
        asgmt_path = os.path.join("projects", f"p{args.project}")
        asgmt_type += 1
        asgmt_num = int(args.project)
    elif args.homework:
        asgmt_path = os.path.join("homework", f"hw{args.homework}")
        asgmt_type += 2
        asgmt_num = int(args.homework)
    else:
        msg.fatal("Missing arguments. Use -h or --help for usage.")

    msg.info("Starting service...")

    # Paths
    root_path = os.getcwd()
    cs_path = util.get_setting("checkstyle")
    lib_path = os.path.join(root_path, util.get_setting('lib'))

    os.chdir(asgmt_path)
    abs_asgmt_path = os.path.abspath(os.getcwd())
    ts_path = os.path.join(abs_asgmt_path, util.get_setting("ts_test_path"))

    precheck()
    rename()
    if asgmt_type == ASGMT_HW:
        hw(args.homework)
    else:
        # javac_all()
        run_all()
