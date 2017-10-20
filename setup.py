#!/usr/bin/env python

from setuptools import setup, find_packages


def main():
    setup(
        name='unmo',
        version='0.2.3',
        description='A legacy chat bot written in pure python',
        author='sandmark',
        author_email='sandmark.m@gmail.com',
        packages=find_packages(),
        install_requires=[
            'janome',
            'tqdm',
            'dill',
        ],
        entry_points={
            'console_scripts': [
                'unmo = cli:main',
            ],
        }
    )


if __name__ == '__main__':
    main()
