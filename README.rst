telegraph-pgbouncer
===================
Poll `pgBouncer <http://pgbouncer.github.io>`_ for stats to submit to
`Telegraf <https://github.com/influxdata/telegraf>`_ using the
`Exec Input Plugin <https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec>`_.
|Version| |License|

Usage
-----
The application is meant to be used via the Exec Input Plugin

Example Telegraf Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block::

   [[inputs.exec]]
     ## Commands array
     commands = [
       "telegraph-pgbouncer -h localhost -p 6432 -U monitor all"
     ]
     timeout = "5s"
     data_format = "json"

CLI Usage
^^^^^^^^^

.. code-block::

   $ telegraph-pgbouncer --help
   usage: pgBouncer Stats Collector for Telegraf

   positional arguments:
     COMMAND               The SHOW command to run for extracting stats. Choices:
                           all, lists, databases, mem, pools, stats

   optional arguments:
     -h HOST, --host HOST  database server host or socket directory (default: localhost)
     -p PORT, --port PORT  database server port number (default: 5432)
     -U USERNAME, --username USERNAME
                           The PostgreSQL username to operate as (default: pgbouncer)
     -W, --password        Force password prompt (should happen automatically)
                           (default: False)
     -v, --version         output version information, then exit
     -?, --help            show this help, then exit

Authentication
^^^^^^^^^^^^^^
Specify the password in a `.pgpass <https://www.postgresql.org/docs/current/static/libpq-pgpass.html>`_ file
for the application to connect properly without specifying a password.

.. |Version| image:: https://img.shields.io/pypi/v/telegraph-pgbouncer.svg?
   :target: https://pypi.org/project/telegraph-pgbouncer

.. |License| image:: https://img.shields.io/pypi/l/telegraph-pgbouncer.svg?
   :target: https://pypi.org/project/telegraph-pgbouncer
