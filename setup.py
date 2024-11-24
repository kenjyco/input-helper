from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

with open('requirements-ipython.txt', 'r') as fp:
    requirements_ipython = fp.read().splitlines()

with open('requirements-xmljson.txt', 'r') as fp:
    requirements_xmljson = fp.read().splitlines()

setup(
    name='input-helper',
    version='0.1.49',
    description='Helpers for parsing user input, generating menus, transforming data, making comparisons, flexible argument acceptance (string to list/set), regex matching, and more',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/input-helper',
    download_url='https://github.com/kenjyco/input-helper/tarball/v0.1.49',
    packages=find_packages(),
    extras_require={
        'ipython': requirements_ipython,
        'xmljson': requirements_xmljson,
        'full': requirements_ipython + requirements_xmljson,
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Shells',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ],
    keywords=['input', 'user input', 'regex', 'matching', 'json', 'selection', 'menus', 'filtering', 'conversions', 'transformations', 'comparisons', 'cli', 'command-line', 'helper', 'kenjyco']
)
