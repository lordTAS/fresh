# Copyright (C) 2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
The API for updating the list of collected hosts.
"""
from Exscript           import Host
from Exscript.util.cast import to_list
import sqlalchemy                 as sa
import sqlalchemy.databases.mysql as mysql

class SeedDB(object):
    """
    The main interface for accessing the database.
    """

    def __init__(self, engine):
        """
        Instantiates a new SeedDB.
        
        @type  engine: object
        @param engine: An sqlalchemy database connection.
        @rtype:  SeedDB
        @return: The new instance.
        """
        self.engine        = engine
        self.metadata      = sa.MetaData(self.engine)
        self._table_prefix = 'seeddb_'
        self._table_map    = {}
        self.__update_table_names()

    def __add_table(self, table):
        """
        Adds a new table to the internal table list.
        
        @type  table: Table
        @param table: An sqlalchemy table.
        """
        pfx = self._table_prefix
        self._table_map[table.name[len(pfx):]] = table

    def __update_table_names(self):
        """
        Adds all tables to the internal table list.
        """
        pfx = self._table_prefix
        self.__add_table(sa.Table(pfx + 'host', self.metadata,
            sa.Column('address',   sa.String(50), primary_key = True),
            sa.Column('name',      sa.String(50)),
            sa.Column('path',      sa.String(50)),
            sa.Column('country',   sa.String(50)),
            sa.Column('city',      sa.String(50)),
            sa.Column('os',        sa.String(50)),
            sa.Column('duration',  sa.Float),
            sa.Column('timestamp',
                      sa.DateTime,
                      default  = sa.func.now(),
                      onupdate = sa.func.now()),
            mysql_engine = 'INNODB'
        ))

    def install(self):
        """
        Installs (or upgrades) database tables.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        self.metadata.create_all()
        return True

    def uninstall(self):
        """
        Drops all tables from the database. Use with care.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        self.metadata.drop_all()
        return True

    def clear_database(self):
        """
        Drops the content of any database table used by this library.
        Use with care.

        Wipes out everything, including types, actions, resources and acls.

        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        delete = self._table_map['order'].delete()
        delete.execute()
        return True

    def debug(self, debug = True):
        """
        Enable/disable debugging.

        @type  debug: Boolean
        @param debug: True to enable debugging.
        """
        self.engine.echo = debug

    def set_table_prefix(self, prefix):
        """
        Define a string that is prefixed to all table names in the database.
        Default is 'guard_'.

        @type  prefix: string
        @param prefix: The new prefix.
        """
        self._table_prefix = prefix
        self.__update_table_names()

    def get_table_prefix(self):
        """
        Returns the current database table prefix.
        
        @rtype:  string
        @return: The current prefix.
        """
        return self._table_prefix

    def __host2dict(self, host, fields = None):
        all = dict(address  = host.get_address(),
                   name     = host.get_name(),
                   path     = host.get('path'),
                   country  = host.get('country'),
                   city     = host.get('city'),
                   os       = host.get('os'),
                   duration = host.get('duration'))
        if fields is None:
            return all
        return dict((k, v) for (k, v) in all.iteritems() if k in fields)

    def __add_host(self, host):
        """
        Inserts the given host into the database.
        """
        if host is None:
            raise AttributeError('host argument must not be None')

        # Insert the host.
        insert = self._table_map['host'].insert()
        result = insert.execute(**self.__host2dict(host))
        return result.last_inserted_ids()[0]

    def __save_host(self, host, fields):
        """
        Inserts or updates the given host into the database.
        """
        if host is None:
            raise AttributeError('host argument must not be None')

        # Check if the host already exists.
        table   = self._table_map['host']
        where   = sa.and_(table.c.address == host.get_address())
        thehost = table.select(where).execute().fetchone()
        fields  = self.__host2dict(host, fields)

        # Insert or update it.
        if thehost is None:
            query   = table.insert()
            result  = query.execute(**fields)
            host_id = result.last_inserted_ids()[0]
        else:
            query   = table.update(where)
            result  = query.execute(**fields)
            host_id = thehost[table.c.address]

        return host_id

    def __get_host_from_row(self, row):
        assert row is not None
        tbl_h = self._table_map['host']
        host  = Host(row[tbl_h.c.address])
        host.set_name(row[tbl_h.c.name])
        host.set('path',     row[tbl_h.c.path])
        host.set('country',  row[tbl_h.c.country])
        host.set('city',     row[tbl_h.c.city])
        host.set('os',       row[tbl_h.c.os])
        host.set('duration', row[tbl_h.c.duration])
        return host

    def __get_hosts_from_query(self, query):
        """
        Returns a list of hosts.
        """
        assert query is not None
        result = query.execute()

        tbl_h     = self._table_map['host']
        host_list = []
        for row in result:
            host = self.__get_host_from_row(row)
            host_list.append(host)

        return host_list

    def __get_conditions(self, **kwargs):
        tbl_h = self._table_map['host']
        where = None

        for field in ('address',
                      'name',
                      'path',
                      'country',
                      'city',
                      'os',
                      'duration'):
            if kwargs.has_key(field):
                cond = None
                for value in to_list(kwargs.get(field)):
                    cond = sa.or_(cond, tbl_h.c[field] == value)
                where = sa.and_(where, cond)

        return where

    def get_host(self, **kwargs):
        """
        Like get_hosts(), but
          - Returns None, if no match was found.
          - Returns the order, if exactly one match was found.
          - Raises an error if more than one match was found.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_hosts().
        @rtype:  Host
        @return: The host or None.
        """
        result = self.get_hosts(0, 2, **kwargs)
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise Exception('Too many results')
        return result[0]

    def get_hosts(self, offset = 0, limit = 0, **kwargs):
        """
        Returns all hosts that match the given criteria.
        
        @type  offset: int
        @param offset: The offset of the first item to be returned.
        @type  limit: int
        @param limit: The maximum number of items that is returned.
        @type  kwargs: dict
        @param kwargs: The following keys may be used:
                         - hostname - the hostname (str)
                         - address - the host address (str)
                         - path - the path (str)
                         - country - the country (str)
                         - city - the city (str)
                         - os - the operation system (str)
                       All values may also be lists (logical OR).
        @rtype:  list[Host]
        @return: The list of hosts.
        """
        tbl_h  = self._table_map['host']
        where  = self.__get_conditions(**kwargs)
        select = tbl_h.select(where)
        return self.__get_hosts_from_query(select)

    def add_host(self, hosts):
        """
        Inserts the given hosts into the database.

        @type  orders: Host|list[Host]
        @param orders: The hosts to be added.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if hosts is None:
            raise AttributeError('hosts argument must not be None')
        for host in to_list(hosts):
            self.__add_host(host)
        return True

    def save_host(self, hosts, fields = None):
        """
        Updates the given hosts in the database. Does nothing if
        the host doesn't exist.
        If fields is a tuple of column names, only the fields with
        the given names are updated.

        @type  hosts: Host|list[Host]
        @param hosts: The host to be saved.
        @rtype:  Boolean
        @return: True on success, False otherwise.
        """
        if hosts is None:
            raise AttributeError('hosts argument must not be None')
        for host in to_list(hosts):
            self.__save_host(host, fields)
        return True

    def delete_host(self, **kwargs):
        """
        Deletes all hosts that match the given criteria.

        @type  kwargs: dict
        @param kwargs: For a list of allowed keys see get_hosts().
        """
        where  = self.__get_conditions(**kwargs)
        delete = self._table_map['host'].delete(where)
        result = delete.execute()

    def delete_old_hosts(self, timestamp):
        """
        Deletes all hosts that have a timestamp that is smaller than
        the given value.

        @type  timestamp: datetime.datetime
        @param timestamp: A Python datetime object.
        """
        tbl_h  = self._table_map['host']
        delete = tbl_h.delete(tbl_h.c.timestamp < timestamp)
        result = delete.execute()
