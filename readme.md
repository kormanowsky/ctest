# CTest 
A Python script which builds and tests your C programs.

## Installation 

1. Download ctest.py and rename it to somewhere in your `PATH`, 
e. g. `/usr/local/bin/ctest`
2. Run ctest: `ctest <your_c_file_name>`

## Configuration 
Add `ctestconfig.json` to your directory. You are able to configure the script
by settings configuration options provided in `default_config` variable.

## Output example 

```bash
CTest tester script

Building /Users/mikhail/PycharmProjects/ctest/main.c using gcc-7 ...
Built /Users/mikhail/PycharmProjects/ctest/main.c to /Users/mikhail/PycharmProjects/ctest/main.exe

Testing /Users/mikhail/PycharmProjects/ctest/main.exe ...

Positive tests:
01: passed

Negative tests:
02: passed

Tested /Users/mikhail/PycharmProjects/ctest/main.exe

Running coverage for /Users/mikhail/PycharmProjects/ctest/main.c ...
-.gcno:cannot open notes file
b.gcno:cannot open notes file
File '/Users/mikhail/PycharmProjects/ctest/main.c'
Lines executed:100.00% of 6
Creating 'main.c.gcov'

Lines executed:100.00% of 6
Ran coverage for /Users/mikhail/PycharmProjects/ctest/main.c
Done!
``` 