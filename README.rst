Waves-Gateway-Framework
=========================

A framework to connect other cryptocurrencies to the Waves platform.
Requires Python 3.5 or newer.

For detailed usage instructions please refer to the source code documentation that may be exported
by using the commands described below.
The framework exports a class Gateway. This class has to instantiated.
Once done, the Gateway can be started by calling the run method on the resulting instance.

The constructor of the Gateway class requires instances of certain interfaces.
Those interfaces define the required functionality that a concrete Gateway implementation has to provide.
You may also take a look at an example implementation that
realizes a Waves-Gateway for Litecoin: https://github.com/jansenmarc/WavesGatewayLTCExample.

How to install
---------------

.. code:: bash

    pip install waves-gateway

Required packages for development
---------------------------------

.. code:: bash

    python3.5 -m pip install coverage mypy pylint Sphinx

Lint
----

The `PyLint <https://www.pylint.org>`__ package is required for linting.
Install it like this: ``pip install pylint``.

.. code:: bash

    python3.5 setup.py lint

MyPy
----

The `MyPy <https://github.com/python/mypy>`__ package performs static
type analysis to prevent errors.

::

    python3.5 setup.py mypy

Unittest
--------

.. code:: bash

    python3.5 setup.py test

The convention is to write Unittests for every class in a separate file
starting with ``test_`` This is the default prefix of the python
Unittest module.

Coverage
--------

.. code:: bash

    python3.5 setup.py coverage

Documentation Generation
========================

Creates a folder docs with the generated HTML documentation.

.. code:: bash

    pip install . -U
    python3.5 setup.py docs

Doctest
-------

Doctests are not used in this project. Write Unittests instead.

yapf
----

This project uses yapf (https://github.com/google/yapf) as a formatting
tool So, please format your code before commiting by running this:

.. code:: bash

    python3.5 -m yapf -r waves_gateway --style pep8 --style {COLUMN_LIMIT:120} -i

The pipeline will fail if the code is not properly formatted.

Distribution
------------

First, run ``npm run build:prod`` to update the assets.
After that, run ``python3.5 setup.py sdist`` to create an installable tar archive.

Publish to test.pypi.org:

.. code:: bash

    twine upload --repository-url https://test.pypi.org/legacy/ dist/*

Regular publish:

.. code:: bash

    twine upload dist/*

Recommendations
---------------

-  Use Python 3.5 for development.
-  PyCharm users should enable Gevent compatible debugging:
   https://blog.jetbrains.com/pycharm/2012/08/gevent-debug-support/.
