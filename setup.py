#!/bin/env python
from setuptools import setup, find_packages
import os 

setup(
    name='django-caldav',
    version='0.1',
    description='CalDAV implementation for Django offering Feed interface',
    author='Petr Knap',
    author_email='knap@wpj.cz',
    url = 'http://www.wpj.cz',
    download_url='',
    packages=["django_caldav",],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Commercial',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
    install_requires = [
        'django',
        'django-ical',
        'django-dav',
        'lxml',
    ],
)
