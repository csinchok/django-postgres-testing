import copy
import shutil
import signal
import subprocess
import os
import tempfile
import psycopg2
import os.path
from glob import glob

from contextlib import closing

from django.db import connections
from django.test.runner import DiscoverRunner


SEARCH_PATHS = (['/usr/local/pgsql', '/usr/local'] +
                glob('/usr/lib/postgresql/*') +  # for Debian/Ubuntu
                glob('/opt/local/lib/postgresql*'))  # for MacPorts


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


class TemporaryPostgresRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):

        postgres_binary_path = os.environ.get('TEMPORARY_POSTGRES_PATH')

        if not postgres_binary_path:
            # Try to find the initdb binary
            initdb_path = shutil.which('initdb')
            if initdb_path:
                postgres_binary_path = os.path.dirname(initdb_path)
            else:
                for base_dir in SEARCH_PATHS:
                    path = os.path.join(base_dir, 'bin', 'initdb')
                    if os.path.exists(path):
                        postgres_binary_path = os.path.join(base_dir, 'bin')
                        break

        self.postgres_socket_directory = tempfile.mkdtemp(prefix='pgsocket')
        self.postgres_directory = tempfile.mkdtemp(prefix='pgdata')
        self.postgres_port = get_open_port()

        print('Initializing test Postgresql cluster...')
        initdb_args = [
            os.path.join(postgres_binary_path, 'initdb'),
            '-A', 'trust',
            '-U', 'postgres',
            '--nosync',
            '-D', self.postgres_directory
        ]
        # Create the database...
        init_process = subprocess.Popen(
            initdb_args,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        init_process.wait()

        if init_process.returncode != 0:
            raise Exception('Couldn\'t  initialize database')

        print('Starting test Postgresql cluster...')
        postgres_args = [
            os.path.join(postgres_binary_path, 'postgres'),
            '-h 127.0.0.1',
            '-F',
            '-p', str(self.postgres_port),
            '-D', self.postgres_directory,
            '-k', self.postgres_socket_directory
        ]
        self.postgres_process = subprocess.Popen(
            postgres_args,
            bufsize=1,
            universal_newlines=1,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        self._old_databases = copy.copy(connections.databases)

        for name, settings in self._old_databases.items():
            connections.databases[name]['HOST'] = 'localhost'
            connections.databases[name]['PORT'] = self.postgres_port
            connections.databases[name]['USER'] = 'postgres'

        # Let postgres start up...
        while True:
            try:
                with closing(
                    psycopg2.connect(
                        host='localhost',
                        port=self.postgres_port,
                        user='postgres'
                    )
                ):
                    pass
            except psycopg2.OperationalError:
                # if not self.postgres_process.poll():
                    # raise Exception('Couldn\'t start postgres')
                continue
            else:
                break

        return super(TemporaryPostgresRunner, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        ret = super(TemporaryPostgresRunner, self).teardown_databases(
            old_config, **kwargs
        )

        self.postgres_process.send_signal(signal.SIGINT)
        self.postgres_process.wait()

        shutil.rmtree(self.postgres_directory)
        shutil.rmtree(self.postgres_socket_directory)
        return ret
