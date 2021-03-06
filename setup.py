# coding=utf-8
from setuptools import setup

from telegraf_pgbouncer import __version__

setup(name='telegraf-pgbouncer',
      version=__version__,
      description='pgBouncer Stats Collector for Telegraf',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: BSD License',
          'Topic :: System :: Monitoring'
      ],
      keywords='static website generation',
      author='Gavin M. Roy',
      author_email='gavinmroy@gmail.com',
      url='https://github.com/gmr/telegraf-pgbouncer',
      license='BSD',
      packages=['telegraf_pgbouncer'],
      package_data={'': ['LICENSE', 'README.rst']},
      include_package_data=True,
      install_requires=[
          'psycopg2-binary'
      ],
      entry_points=dict(console_scripts=[
          'telegraf-pgbouncer=telegraf_pgbouncer.cli:main']),
      zip_safe=True)
