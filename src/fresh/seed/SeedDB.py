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
from Exscript import Host, Account, PrivateKey
from Exscript.util.cast import to_list
import sqlalchemy as sa
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
            sa.Column('name',      sa.String(50), primary_key = True),
            sa.Column('address',   sa.String(50)),
            sa.Column('protocol',  sa.String(10)),
            sa.Column('tcp_port',  sa.Integer),
            sa.Column('path',      sa.String(150)),
            sa.Column('country',   sa.String(50)),
            sa.Column('city',      sa.String(50)),
            sa.Column('os',        sa.String(50)),
            sa.Column('duration',  sa.Float),
            sa.Column('deleted',   sa.Boolean, default = False),
            sa.Column('timestamp',
                      sa.DateTime,
                      default  = sa.func.now(),
                      onupdate = sa.func.now()),
            mysql_engine = 'INNODB'
        ))

        self.__add_table(sa.Table(pfx + 'account', self.metadata,
            sa.Column('host',          sa.String(50), primary_key = True),
            sa.Column('name',          sa.String(50)),
            sa.Column('password',      sa.String(50)),
            sa.Column('skey_password', sa.String(50)),
            sa.Column('authorization_password',  sa.String(50)),
            sa.Column('keyfile',       sa.String(50)),
            sa.ForeignKeyConstraint(['host'],
                                    [pfx + 'host.name'],
                                    ondelete = 'CASCADE'),
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
                   protocol = host.get_protocol(),
                   tcp_port = host.get_tcp_port(),
                   path     = host.get('path'),
                   country  = host.get('country'),
                   city     = host.get('city'),
                   os       = host.get('os'),
                   duration = host.get('duration'),
                   deleted  = host.get('deleted'))
        if fields is None:
            return all
        return dict((k, v) for (k, v) in all.iteritems() if k in fields)

    def __account2dict(self, account, fields = None):
        pw2     = account.authorization_password
        key     = account.get_key()
        keyfile = key is not None and key.get_filename() or None
        all = dict(name                   = account.get_name(),
                   password               = account.get_password(),
                   authorization_password = pw2,
                   skey_password          = None, # TODO: account.get_skey_password(),
                   keyfile                = keyfile)
        if fields is None:
            return all
        return dict((k, v) for (k, v) in all.iteritems() if k in fields)

    def __add_host(self, host):
        """
        Inserts the given host into the database.
        """
        if host is None:
            raise AttributeError('host argument must not be None')
        account = host.get_account()

        # Insert the host.
        with self.engine.contextual_connect(close_with_result = True).begin():
            insert = self._table_map['host'].insert()
            insert.execute(**self.__host2dict(host))

            if account:
                insert = self._table_map['account'].insert()
                insert.execute(**self.__account2dict(account))

    def __save_host(self, host, host_fields, account_fields):
        """
        Inserts or updates the given host into the database.
        """
        if host is None:
            raise AttributeError('host argument must not be None')

        # Check if host and account already exist.
        tbl_h       = self._table_map['host']
        tbl_a       = self._table_map['account']
        table       = tbl_h.outerjoin(tbl_a, tbl_h.c.name == tbl_a.c.host)
        where       = sa.and_(tbl_h.c.name == host.get_name())
        query       = sa.select([tbl_h.c.name, tbl_a.c.host.label('account')],
                                where,
                                from_obj = [table])

        row         = query.execute().fetchone()
        host_fields = self.__host2dict(host, host_fields)

        # Insert or update the host.
        if row is None:
            query        = tbl_h.insert()
            result       = query.execute(**host_fields)
            host_id      = result.last_inserted_ids()[0]
            have_account = False
        else:
            query        = tbl_h.update(where)
            result       = query.execute(**host_fields)
            host_id      = row[tbl_h.c.name]
            have_account = row['account'] is not None

        # If the host has no account specified, remove the account
        # from the DB (if any).
        account = host.get_account()
        if account is None:
            if have_account:
                query  = tbl_a.delete(host == host_id)
                result = query.execute()
            return host_id

        # Else insert or update the account.
        account_fields = dict(**self.__account2dict(account, account_fields))
        if have_account:
            query  = tbl_a.update(tbl_a.c.host == host_id)
            result = query.execute(**account_fields)
        else:
            query  = tbl_a.insert()
            result = query.execute(host = host_id, **account_fields)

        return host_id

    def __get_host_from_row(self, row):
        assert row is not None
        tbl_h = self._table_map['host']
        host  = Host(row[tbl_h.c.name])
        host.set_address(row[tbl_h.c.address])
        host.set_protocol(row[tbl_h.c.protocol])
        host.set_tcp_port(row[tbl_h.c.tcp_port])
        host.set('path',     row[tbl_h.c.path])
        host.set('country',  row[tbl_h.c.country])
        host.set('city',     row[tbl_h.c.city])
        host.set('os',       row[tbl_h.c.os])
        host.set('duration', row[tbl_h.c.duration])
        host.set('deleted',  row[tbl_h.c.deleted])
        return host

    def __get_account_from_row(self, row):
        assert row is not None
        tbl_a = self._table_map['account']
        if row[tbl_a.c.host] is None:
            return None

        key     = PrivateKey.from_file(row[tbl_a.c.keyfile])
        account = Account(row[tbl_a.c.name], key = key)
        account.set_password(row[tbl_a.c.password])
        account.set_authorization_password(row[tbl_a.c.authorization_password])
        #TODO: account.set_skey_password(row[tbl_a.c.skey_password])
        return account

    def __get_hosts_from_query(self, query, filter = None):
        """
        Returns a list of hosts.
        """
        assert query is not None
        result    = query.execute()
        host_list = []
        for row in result:
            host    = self.__get_host_from_row(row)
            account = self.__get_account_from_row(row)
            host.set_account(account)
            if filter is None or filter(host) is True:
                host_list.append(host)

        return host_list

    def __get_conditions(self, **kwargs):
        tbl_h = self._table_map['host']
        where = None

        for field in ('address',
                      'name',
                      'protocol',
                      'tcp_port',
                      'path',
                      'country',
                      'city',
                      'os',
                      'duration',
                      'deleted'):
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
            raise ValueError('Too many results')
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
                         - protocol - the protocol name (str)
                         - tcp_port - the TCP port number (int)
                         - path - the path (str)
                         - country - the country (str)
                         - city - the city (str)
                         - os - the operation system (str)
                         - deleted - the 'deleted' flag (bool)
                       All values may also be lists (logical OR).
        @rtype:  list[Host]
        @return: The list of hosts.
        """
        tbl_h  = self._table_map['host']
        tbl_a  = self._table_map['account']
        table  = tbl_h.outerjoin(tbl_a, tbl_h.c.name == tbl_a.c.host)
        where  = self.__get_conditions(**kwargs)
        select = table.select(where, use_labels = True)
        return self.__get_hosts_from_query(select)

    def get_hosts_from_filter(self, filter, **kwargs):
        """
        Iterates over all hosts, passing them to the given callback function.
        If the callback returns True, the host is included in the returned
        list.

        @type  filter: function
        @param filter: A callback function that is called once for each host.
        @type  kwargs: dict
        @param kwargs: See get_hosts()
        @rtype:  list[Host]
        @return: The list of hosts for which the callback returned True.
        """
        tbl_h  = self._table_map['host']
        tbl_a  = self._table_map['account']
        table  = tbl_h.outerjoin(tbl_a, tbl_h.c.name == tbl_a.c.host)
        where  = self.__get_conditions(**kwargs)
        select = table.select(where, use_labels = True)
        return self.__get_hosts_from_query(select, filter = filter)

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
            self.__save_host(host, fields, None)
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

    def mark_old_hosts(self, timestamp):
        """
        Marks all hosts that have a timestamp that is smaller than
        the given value as deleted.

        @type  timestamp: datetime.datetime
        @param timestamp: A Python datetime object.
        """
        tbl_h  = self._table_map['host']
        query  = tbl_h.update(tbl_h.c.timestamp < timestamp)
        result = query.execute(deleted = True)
