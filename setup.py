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
            'freecritters_db_version = freecritters.db_versioning:main'
        ]
    },
    include_package_data=True,
    zip_safe=False, # Sigh...
    install_requires=['Jinja>=1.2', 'SQLAlchemy>=0.4',
                      'PyYAML>=3.0', 'Werkzeug>=0.1dev', 'simplejson>=1.5',
		              'PIL>=1.1.5']
)
