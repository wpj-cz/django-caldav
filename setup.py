#!/bin/env python
from setuptools import setup, find_packages
import os 

setup(
    name='django-caldav',
    version='0.3',
    description='CalDAV implementation for Django offering Feed interface',
    author='Petr Knap',
    author_email='knap@wpj.cz',
    url = 'http://www.wpj.cz',
    download_url='',
    packages=["django_caldav",],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business',
    ],
    zip_safe = False,
    install_requires = [
        'django',
        'django-ical',
        'djangodav>=0.0.1b5',
        'lxml',
    ],
)
