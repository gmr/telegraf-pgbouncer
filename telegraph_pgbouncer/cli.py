# coding=utf-8
"""
CLI Application for telegraph-pgbouncer

"""
import argparse
import getpass
import json
import sys

import psycopg2
from psycopg2 import extras

from telegraph_pgbouncer import __version__

COMMANDS = {
    'all',
    'databases',
    'lists',
    'mem',
    'pools',
    'stats'
}


def exit_application(message=None, code=0):
    """Exit the application displaying the message to either stdout or stderr
    based upon the exist code.

    :param str message: The exit message
    :param int code: The exit code (default: 0)

    """
    if message:
        if code:
            sys.stderr.write('{}\n'.format(message.strip()))
        else:
            sys.stdout.write('{}\n'.format(message.strip()))
    sys.exit(code)


def main():
    """Application entry point"""
    PgBouncerStats(parse_cli_arguments()).run()


def parse_cli_arguments():
    """Return the base argument parser for CLI applications.


    :return: :class:`~argparse.ArgumentParser`

    """
    parser = argparse.ArgumentParser(
        'telegraph-pgbouncer',
        'pgBouncer Stats Collector for Telegraf',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve')
    parser.add_argument('-h', '--host', action='store', type=str,
                        default='localhost',
                        help='database server host or socket directory')
    parser.add_argument('-p', '--port', action='store', type=int, default=5432,
                        help='database server port number')
    parser.add_argument('-U', '--username', action='store',
                        default=getpass.getuser(),
                        help='The PostgreSQL username to operate as')
    parser.add_argument('-W', '--password', action='store_true',
                        help='Force password prompt '
                             '(should happen automatically)')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(__version__),
                        help='output version information, then exit')
    parser.add_argument('-?', '--help', action='help',
                        help='show this help, then exit')
    parser.add_argument('command', metavar='COMMAND', choices=COMMANDS,
                        default='all',
                        help='The SHOW command to run for extracting stats. '
                             'Choices: {}'.format(', '.join(COMMANDS)))
    return parser.parse_args()


def transform_databases(values):
    """Transform the output of databases to something more manageable.

    :param list values: The list of values from `SHOW DATABASES`
    :rtype: dict

    """
    output = {}
    for row in values:
        if row['database'] not in output:
            output[row['database']] = {}
        mode = row['pool_mode'] or 'default'
        if mode not in output[row['database']]:
            output[row['database']][mode] = {}
        for k, v in row.items():
            if k in ['database', 'force_user', 'host', 'name', 'port',
                     'pool_mode']:
                continue
            output[row['name']][mode][k] = v
    return output


def transform_lists(values):
    """Transform the output of lists to something more manageable.

    :param list values: The list of values from `SHOW LISTS`
    :rtype: dict

    """
    return {row['list']: row['items'] for row in values}


def transform_mem(values):
    """Transform the output of lists to something more manageable.

    :param list values: The list of values from `SHOW MEM`
    :rtype: dict

    """
    output = {}
    for value in values:
        output[value['name']] = {k: v for (k, v) in value.items()
                                 if k != 'name'}
    return output


def transform_pools(values):
    """Transform the output of pools to something more manageable.

    :param list values: The list of values from `SHOW POOLS`
    :rtype: dict

    """
    output = {}
    for row in values:
        if row['database'] not in output:
            output[row['database']] = {}
        if row['user'] not in output[row['database']]:
            output[row['database']][row['user']] = {}
        for k, v in row.items():
            if k in ['database', 'user']:
                continue
            output[row['database']][row['user']][k] = v
    return output


def transform_stats(values):
    """Transform the output of stats to something more manageable.

    :param list values: The list of values from `SHOW STATS`
    :rtype: dict

    """
    output = {}
    for row in values:
        if row['database'] not in output:
            output[row['database']] = {}
        for k, v in row.items():
            if k == 'database':
                continue
            output[row['database']][k] = v
    return output


class PgBouncerStats:

    TRANSFORM = {
        'databases': transform_databases,
        'lists': transform_lists,
        'mem': transform_mem,
        'pools': transform_pools,
        'stats': transform_stats
    }

    def __init__(self, args):
        self.args = args
        self.conn = None
        self.measurements = {}

    def connect(self, password=None):
        """Returns a psycopg2 :class:`~psycopg2.extensions.connection` for
        the specified arguments, with autocommit turned on.

        :param password: The password to use when connecting
        :type password: str or None
        :rtype: :class:`~psycopg2.extensions.connection`

        """
        try:
            conn = psycopg2.connect(host=self.args.host,
                                    port=self.args.port,
                                    user=self.args.username,
                                    password=password,
                                    database='pgbouncer',
                                    cursor_factory=extras.DictCursor)
        except psycopg2.OperationalError as error:
            exit_application(
                'Failed to connect to pgBouncer {}'.format(error), 1)
        conn.autocommit = True
        return conn

    def run(self):
        """Primary Application Behavior"""
        self.conn = self.connect(
            getpass.getpass('pgBouncer Password: ')
            if self.args.password else None)

        if self.args.command == 'all':
            measurements = self.gather_all()
        else:
            measurements = self.gather_command(self.args.command)

        sys.stdout.write(json.dumps(measurements, sort_keys=True, indent=2))

    def gather_all(self):
        """Gather all of the available measurements from pgBouncer, returning
        everything.

        :rtype: dict

        """
        """Gather all of the available measurements"""
        measurements = {}
        for command in [c for c in COMMANDS if c != 'all']:
            measurements[command] = self.gather_command(command)
        return measurements

    def gather_command(self, command):
        """Return the measurements for a single command.

        :param str command: The `SHOW` command to run
        :rtype: list or dict

        """
        cursor = self.conn.cursor()
        cursor.execute('SHOW {}'.format(command.upper()))
        values = [dict(r) for r in cursor]
        if command in self.TRANSFORM:
            return self.TRANSFORM[command](values)
        return values
