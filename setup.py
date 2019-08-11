from distutils.core import setup
from setuptools import find_packages
from distutils.cmd import Command


class CoverageCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess

        code = subprocess.call([
            sys.executable, '-m', 'nose', 'tests', '--with-coverage', '--cover-package', 'waves_gateway',
            '--cover-html'
        ])

        exit(code)


class MyPyCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess

        code = subprocess.call([sys.executable, '-m', 'mypy', 'waves_gateway', '--ignore-missing-imports'])

        exit(code)


class LintCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess

        code = subprocess.call([sys.executable, '-m', 'pylint', 'waves_gateway'])

        exit(code)


class DocsCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess, os, shutil

        if os.path.exists("docs"):
            shutil.rmtree("docs")

        if os.path.exists(".apidoc"):
            shutil.rmtree(".apidoc")

        code = subprocess.call(['sphinx-apidoc', '-o', '.apidoc', 'waves_gateway', '-l', '-F', '-H', 'Waves-Gateway-Framework', '-A', 'Henning Gerrits', '-f'])

        if code != 0:
            exit(code)

        code = subprocess.call(['sphinx-build', '.apidoc', 'docs'])

        open('docs/.nojekyll', 'a').close()

        exit(code)


setup(
    name='waves_gateway',
    url='https://github.com/jansenmarc/WavesGatewayFramework',
    version='1.0.5',
    author='Henning Gerrits',
    test_suite='nose.collector',
    tests_require=['nose'],
    keywords='waves gateway wavesplatform',
    python_requires='>=3.5',
    install_requires=[
        'PyWaves==0.8.24', 'python-doc-inherit>=0.3.0', 'simplejson>=3.11.1', 'requests>=2.9.1', 'base58==0.2.5',
        'pymongo>=3.4.0', 'Flask>=0.12.2', 'gevent>=1.2.2'
    ],
    description='A framework to connect other cryptocurrencies to the Waves-Platform.',
    package_data={'waves_gateway': ['static/**/*', 'static/*']},
    license='MIT',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests']),
    cmdclass={
        'coverage': CoverageCommand,
        'mypy': MyPyCommand,
        'lint': LintCommand,
        'docs': DocsCommand
    })
