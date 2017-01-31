from setuptools import setup


with open('README.rst', 'r') as fp:
    long_description = fp.read()

setup(
    name='input-helper',
    version='0.1.1',
    description='Common CLI input helper functions and string/arg conversions',
    long_description=long_description,
    author='Ken',
    author_email='kenjyco@gmail.com',
    license='MIT',
    url='https://github.com/kenjyco/input-helper',
    download_url='https://github.com/kenjyco/input-helper/tarball/v0.1.1',
    packages=['input_helper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
    ],
    keywords = ['input', 'cli', 'helper']
)

