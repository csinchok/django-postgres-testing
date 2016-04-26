import copy
import shutil
import subprocess
import tempfile
import time
import psycopg2

from contextlib import closing

from django.db import connections
from django.test.runner import DiscoverRunner


INITDB = '/usr/local/bin/initdb'


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

        self.postgres_directory = tempfile.mkdtemp(prefix='postgres')
        self.postgres_port = get_open_port()
        initdb_args = [
            'initdb',
            '-A', 'trust',
            '-U', 'postgres',
            '-D', self.postgres_directory
        ]
        # Create the database...
        init_process = subprocess.Popen(
            initdb_args,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        init_process.wait()

        postgres_args = [
            'postgres',
            '-h 127.0.0.1',
            '-F',
            # '-c', 'logging_collector=false'
            '-p', str(self.postgres_port),
            '-D', self.postgres_directory
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
                continue
            else:
                break

        return super(TemporaryPostgresRunner, self).setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        ret = super(TemporaryPostgresRunner, self).teardown_databases(
            old_config, **kwargs
        )

        self.postgres_process.kill()
        self.postgres_process.wait()

        shutil.rmtree(self.postgres_directory)

        return ret
