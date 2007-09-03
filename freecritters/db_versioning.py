# -*- coding: utf-8 -*-

from storm.locals import *
from urlparse import urlparse
import yaml
import os.path
import sys

class Error(Exception):
    pass
    
class UnknownDatabaseError(Error):
    pass

class UnknownMetaversionError(Error):
    pass

class VersioningTableError(Error):
    pass

class TooHighVersionError(Error):
    pass

class DatabaseVersioner(object):
    def __init__(self, yaml_filename, db_url):
        yaml_file = open(yaml_filename)
        try:
            info = yaml.load(yaml_file.read())
        finally:
            yaml_file.close()
        self.version = int(info.get('version', -1))
        if self.version is None:
            self.version = -1
        self.version_dir = os.path.join(os.path.dirname(yaml_filename), info.get('path', ''))
        
        if urlparse(db_url)[0] != 'postgres':
            raise UnknownDatabaseError('PostgreSQL is the only supported database at the moment.')
        database = create_database(db_url)
        self.conn = database.connect()
    
    def database_version(self):
        table_count, = self.conn.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public' AND tablename='db_versioning'").get_one()
        if table_count:
            meta_version = self.conn.execute('SELECT meta_version FROM public.db_versioning').get_one()
            if meta_version is None:
                return None
            meta_version, = meta_version
            if meta_version != 0:
                raise UnknownMetaversionError('Unknown meta-version %s. This database is from the future.\n' % meta_version)
            version_cursor = self.conn.execute('SELECT version FROM public.db_versioning')
            version, = version_cursor.get_one()
            if version_cursor.get_one():
                raise VersioningTableError("Invalid versioning table: more than one row. Backup your database and cry.\n")
            if version > self.version:
                raise TooHighVersionError("Database version is %s, but the highest version I know about is %s." % (version, self.version))
            return version
        else:
            return None
    
    def close(self):
        self.conn.close()
    
    def _apply_version(self, subdir, n):
        sql_filename = os.path.join(self.version_dir, subdir, '%s.sql' % n)
        py_filename = os.path.join(self.version_dir, subdir, '%s.py' % n)
        def run_sql():            
            try:
                f = open(sql_filename)
            except IOError:
                return
            try:
                sql = f.read()
            finally:
                f.close()
            self.conn.execute(sql, noresult=True)
        try:
            execfile(py_filename, {'run_sql': run_sql, 'conn': self.conn})
        except IOError:
            run_sql()
    
    def _add_version_control(self):
        sys.stdout.write('Adding versioning information to database...\n')
        table_count, = self.conn.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public' AND tablename='db_versioning'").get_one()
        if not table_count:
            self.conn.execute('''
            CREATE TABLE public.db_versioning (
                meta_version INTEGER NOT NULL,
                version INTEGER NOT NULL
            );
            ''')
        self.conn.execute('''
        INSERT INTO public.db_versioning(meta_version, version) VALUES(0, -1);
        ''')
    
    def upgrade(self, new_version):
        new_version = min(new_version, self.version)
        db_version = self.database_version()
        if db_version is None:
            self._add_version_control()
            db_version = -1
        for temp_version in xrange(db_version + 1, new_version + 1):
            sys.stdout.write('Upgrading to version %s...\n' % temp_version)
            self._apply_version('upgrade', temp_version)
        if new_version > db_version:
            self.conn.execute('UPDATE public.db_versioning SET version=%s', (new_version, ), noresult=True)
        self.conn.commit()
    
    def downgrade(self, new_version):
        new_version = max(new_version, -1)
        db_version = self.database_version()
        if db_version is None:
            self._add_version_control()
            db_version = -1
        for temp_version in xrange(db_version, new_version, -1):
            sys.stdout.write('Downgrading from version %s...\n' % temp_version)
            self._apply_version('downgrade', temp_version)
        if new_version < db_version:
            self.conn.execute('UPDATE public.db_versioning SET version=%s', (new_version, ), noresult=True)
        self.conn.commit()

def help(name):
    sys.stdout.write(
'''Usage:\n
    $ upgrade db_url [version]:
        Upgrades to the specified version. If no version number is
        specified, upgrades to the highest version.
        
    $ downgrade db_url version:
        Downgrades to the specified version. If the version is -1,
        removes the entire schema.
        
    $ check_version db_url:
        Prints the database's current version number.
        
    $ help:
        Prints this.
'''.replace('$', name))

def main(argv):
    if len(argv) < 2:
        sys.stderr.write('Command is required. Try `%s help`.\n' % argv[0])
        return 1
    command = argv[1]
    try:
        if command in ('upgrade', 'downgrade', 'check_version'):
            if len(argv) < 3:
                sys.stderr.write('I need a database URL.\n')
                return 1
            db_url = sys.argv[2]
            versioner = DatabaseVersioner(os.path.join(os.path.dirname(__file__), 'schema/schema.yaml'), db_url)
            try:
                if command == 'check_version':
                    sys.stdout.write('Current database version: %s\n' % versioner.database_version())
                elif command == 'upgrade':
                    if len(argv) < 4:
                        version = versioner.version
                    else:
                        try:
                            version = int(argv[3])
                        except ValueError:
                            sys.stderr.write('Invalid version number.\n')
                            return 1
                    versioner.upgrade(version)
                elif command == 'downgrade':
                    if len(argv) < 4:
                        sys.stderr.write('Need a version number for downgrades.\n')
                        return 1
                    try:
                        version = int(argv[3])
                    except ValueError:
                        sys.stderr.write('Invalid version number.\n')
                        return 1
                    versioner.downgrade(version)
            finally:
                versioner.close()
        elif command == 'help':
            help(argv[0])
        else:
            sys.stderr.write('Unknown command. Try `%s help`.\n' % argv[0])
    except Error, e:
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        return 1
    except StormError, e:
        sys.stderr.write('Database error: ')
        sys.stderr.write(str(e))
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))