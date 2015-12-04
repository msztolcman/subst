from setuptools import setup, find_packages
from codecs import open
from os import path

BASE_DIR = path.abspath(path.dirname(__file__))

with open(path.join(BASE_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='subst',
    version='0.4.0',
    description='`subst` is simple utility to replace one string into another in given list of files.',
    long_description=long_description,
    url='http://msztolcman.github.io/subst/',
    author='Marcin Sztolcman',
    author_email='marcin@urzenia.net',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['argparse'],
    py_modules=['subst'],

    keywords='sed text processing',

    entry_points={
        'console_scripts': [
            'subst=subst:main',
        ],
    },
)

