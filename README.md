# Waves Gateway Package

A framework to connect other cryptocurrencies to the Waves platform.
Requires Python 3.5 or newer.

## Requires packages for development
```bash
python3.5 -m pip install coverage mypy pylint
```

## Lint
The [PyLint](https://www.pylint.org) package is required for linting.
Install it like this: `pip install pylint`.
```bash
python3.5 setup.py lint
```

## MyPy
The [MyPy](https://github.com/python/mypy) package performs static type analysis to prevent errors.
```
python3.5 setup.py mypy
```

## Unittest
```bash
python3.5 setup.py test
```
The convention is to write Unittests for every class in a separate file
starting with `test_` This is the default prefix of the python Unittest module.

## Coverage
```bash
python3.5 setup.py coverage
```

# Documentation Generation
Creates a folder docs with the generated HTML documentation.
```bash
python3.5 setup.py pydoc
```

## Doctest
Doctests are not used in this project. Write Unittests instead.

## yapf
This project uses yapf (https://github.com/google/yapf) as a formatting tool
So, please format your code before commiting by running this:
```bash
python3.5 -m yapf -r waves_gateway --style pep8 --style {COLUMN_LIMIT:120} -i
```
The pipeline will fail if the code is not properly formatted.

## Recommendations
-   Use Python 3.5 for development.
-   PyCharm users should enable Gevent compatible debugging: https://blog.jetbrains.com/pycharm/2012/08/gevent-debug-support/.
