#!/usr/bin/python
from migrate.versioning.shell import main
import os

def manage():
    main(repository=os.path.dirname(__file__))
