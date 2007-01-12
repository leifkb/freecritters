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
            'freecritters_run_fcgi = freecritters.web.run:run_fcgi',
            'freecritters_db_manage = freecritters.dbrepo.manage:manage'
        ]
    },
    include_package_data=True,
    zip_safe=False, # Sigh...
    install_requires=['Jinja>=0.9', 'migrate>=0.2', 'SQLAlchemy>=0.3',
                      'PyYAML>=3.0', 'Colubrid>=0.10']
)
