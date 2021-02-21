#! python3
"""
A script which builds and tests C programs
Author: M. Kormanowsky
Version: 1.0.0
Date: 21.02.2021
"""
from argparse import ArgumentParser
from pathlib import Path
from json import loads
from subprocess import Popen, run
from sys import stderr
from re import compile


class Colors:
    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


dirname = Path.cwd()
config_file_name = "ctestconfig.json"
default_config = {
    "compiler": "gcc",
    "args": "--std=c99 -Wall -Werror "
            "-Wfloat-conversion -Wfloat-equal --coverage",
    "coverage_meter": "gcov",
    "coverage_meter_args": "-b",
    "tests_dir": "func_tests",
    "test_file_regex": "(pos|neg)_([0-9]{2})_(in|out)\.txt",
    "tests_encoding": "utf-8"
}


def get_file_name() -> str:
    """
    Gets the name of the file from the user
    :return: Received file name as string
    """
    parser = ArgumentParser(description="Build & test your C programs")
    parser.add_argument("file", type=str, help="The path to your C file")
    args = parser.parse_args()
    return args.file


def get_config() -> dict:
    """
    Gets the configuration, merging default and specified in
    ctestconfig.json
    :return: Merged config as dict
    """
    config = default_config
    config_path = dirname / config_file_name
    if Path.exists(config_path):
        with open(config_path, "r") as config_file:
            config.update(loads(config_file.read()))
    return config


def build(file_path, config):
    """
    Builds given c file using given config
    :param file_path: A path to file to build
    :param config: A config to use
    :return: A path to built executable
    """
    executable_path = str(file_path).replace(".c", ".exe")
    compiler_args = [config["compiler"]]
    compiler_args += config["args"].split()
    compiler_args += ["-o", executable_path]
    compiler_args.append(str(file_path))
    print(Colors.ENDC + "Building", file_path, "using", config["compiler"],
          "...")
    process = run(compiler_args, capture_output=True)
    output = process.stdout
    error_output = process.stderr
    if not process.returncode:
        print(Colors.OKGREEN + Colors.BOLD + "Built", file_path, "to",
              executable_path)
        return executable_path
    else:
        print(Colors.FAIL + "Failed building", str(file_path) + Colors.ENDC)
        print(output.decode(config["tests_encoding"]), file=stderr)
        print(error_output.decode(config["tests_encoding"]), file=stderr)


def test(executable_path, tests_path, config) -> None:
    """
    Test given executable file using tests from tests_path and config
    :param executable_path: The executable file path
    :param tests_path: The path to the tests
    :param config: The configuration
    """
    print(Colors.ENDC + "Testing", executable_path, "...")
    test_file_regex = compile(config["test_file_regex"])
    done_tests = []
    test_results = {
        "pos": [],
        "neg": []
    }
    for file in tests_path.iterdir():
        file_name = file.name
        if file_name in done_tests:
            continue
        matches = test_file_regex.search(file_name)
        if matches is None:
            continue
        test_type, index, file_type = matches.groups()
        if file_type == "in":
            input_file = tests_path / file_name
            output_file = tests_path / file_name.replace("in", "out")
            result = single_test(
                executable_path, test_type, input_file, output_file, config
            )
            test_results[test_type].append([index, result])
            done_tests.append(input_file)
            done_tests.append(output_file)
    print()
    print(Colors.ENDC + "Positive tests:")
    for t in list(sorted(test_results["pos"], key=lambda i: i[0])):
        display_test(t)
    print()
    if test_results["neg"]:
        print(Colors.ENDC + "Negative tests:")
        for t in list(sorted(test_results["neg"], key=lambda i: i[0])):
            display_test(t)
        print()
    print(Colors.OKGREEN + Colors.BOLD + "Tested", executable_path)


def single_test(executable_path, test_type, input_file, output_file, config):
    """
    Performs a single test on executable file
    :param executable_path: The path to executable file
    :param test_type: Test type (pos/neg)
    :param input_file: Text file with input data
    :param output_file: Text file with expected output data
    :param config: Configuration
    :return:
    """
    encoding = config["tests_encoding"]
    process = run([executable_path],
                  stdin=open(str(input_file), "r", encoding=encoding),
                  capture_output=True)
    output = process.stdout.decode(encoding)
    error_output = process.stderr.decode(encoding)
    expected_output = open(output_file, "r", encoding=encoding) \
        .read().strip(" \n")
    return_code = process.returncode
    if test_type == "pos" and return_code != 0 or \
            test_type == "neg" and return_code == 0:
        success = False
    else:
        success = output == expected_output
    return success, return_code, output, expected_output, error_output


def display_test(test_data) -> None:
    """
    Displays given test data
    :param test_data: An array containing index and result of the test
    """
    index, result = test_data
    success, code, output, expected_output, error_output = result
    print((Colors.OKGREEN if success else Colors.FAIL) + Colors.BOLD +
          "{}: {}".format(index, "passed" if success else "failed"))
    if not success:
        print(Colors.ENDC + "Exit code: {}".format(code))
        print(Colors.BOLD + "Output:")
        print(Colors.ENDC + output)
        print(Colors.BOLD + "Expected output:")
        print(Colors.ENDC + expected_output)
        print(Colors.BOLD + "Error output:")
        print(Colors.ENDC + error_output)


def coverage(file_path, config) -> None:
    """
    Run coverage meter (usually gcov) for given file
    :param file_path: A path to file
    :param config: The configuration
    """
    print(Colors.ENDC + "Running coverage for", file_path, "...")
    coverage_args = [config["coverage_meter"]]
    coverage_args += config["coverage_meter_args"]
    coverage_args.append(str(file_path))
    run(coverage_args)
    print(Colors.OKGREEN + Colors.BOLD + "Ran coverage for", file_path)


def main():
    print()
    print(Colors.HEADER + Colors.BOLD + "CTest tester script" + Colors.ENDC)
    print()
    file = get_file_name()
    file_path = dirname / file
    config = get_config()
    if not file_path.exists():
        print(Colors.FAIL + "Error: c source file does not exist!", file=stderr)
        return
    tests_path = file_path.parent / config["tests_dir"]
    run_tests = True
    if not tests_path.exists():
        print(Colors.WARNING + "Warning: tests directory", tests_path,
              "does not exist!",
              file=stderr)
        run_tests = False
    executable_path = build(file_path, config)
    if executable_path is None or not run_tests:
        return
    print()
    test(executable_path, tests_path, config)
    print()
    coverage(file_path, config)
    print(Colors.OKGREEN + Colors.BOLD + "Done!" + Colors.ENDC)


if __name__ == "__main__":
    main()
