from setuptools import setup, find_packages


with open('README.rst', 'r') as fp:
    long_description = fp.read()

with open('requirements-ipython.txt', 'r') as fp:
    requirements_ipython = fp.read().splitlines()

with open('requirements-xmljson.txt', 'r') as fp:
    requirements_xmljson = fp.read().splitlines()

setup(
    name='input-helper',
    version='0.1.41',
    description='Common CLI input helper functions and string/arg conversions',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/input-helper',
    download_url='https://github.com/kenjyco/input-helper/tarball/v0.1.41',
    packages=find_packages(),
    extras_require={
        'ipython': requirements_ipython,
        'xmljson': requirements_xmljson,
        'full': requirements_ipython + requirements_xmljson,
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords=['input', 'cli', 'helper']
)
