[![Build Status](https://travis-ci.com/cjneely10/PythonDataStructures.svg?token=M4ut94Kepv6qucNU1mEy&branch=master)](https://travis-ci.com/cjneely10/PythonDataStructures)
[![codecov](https://codecov.io/gh/cjneely10/PythonDataStructures/branch/master/graph/badge.svg?token=VI556SPEZV)](https://codecov.io/gh/cjneely10/PythonDataStructures)

# Various Python Data Structures

This repository contains several data structures that are (somewhat) useful when developing code.

All code is currently in development and is not (particularly) meant for general use...yet

## Installation

```
git clone https://github.com/cjneely10/PythonDataStructures.git
pip install PythonDataStructures
```

## Currently:

### Mutable String

```
data = Str("one")
data[1] = "b"
print(data)  # Outputs "obe"
```

---

### Run-time Type Checking

```
@TypeChecker()
def run(value: int) -> str:
    return str(value)

run("a")  # Raises TypeError

```

---

### Parallel Iteration

```
@iter_threaded(4, value=range(10))
def run(value):
    print(value)

# Calls the function run() using all values in `value` on 4 system threads
# Returns iterator over all results
run()

```

Can also be used as non-decorated function:

```
def run(value):
    print(value)

run_threaded = iter_threaded(4, value=range(10))(run)

run_threaded()

```

Error handling is automated to have "allowed" silent failures

```
@iter_threaded(4, value=range(5), ignore_types=(None,))
def run(value):
    if value != 2:
        print(value)

list(run()) == [0,1,3,4]  # Outputs True
```

---

See the `tests` suite for more examples on using each.

See [the documentation](https://github.com/cjneely10/PythonDataStructures/blob/master/docs/build/latex/pythondatastructures.pdf)
 for more information.
