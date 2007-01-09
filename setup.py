# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="freeCritters",
    version="0.1",
    description="Virtual pets.",
    author="Leif K-Brooks",
    packages=['freecritters'],
    entry_points={
        'console_scripts': [
            'freecritters_run_dev = freecritters.web.run:run_dev',
            'freecritters_run_fcgi = freecritters.web.run:run_fcgi'
        ]
    },
    include_package_data=True
)
