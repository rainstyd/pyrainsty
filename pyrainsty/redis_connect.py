# -*- encoding: utf-8 -*-

"""
@author: rainsty
@file:   redis_connect.py
@time:   2021-10-25 15:43:26
@desc:
"""

import redis
import copy
from redis.sentinel import Sentinel


class RedisConnect(object):

    """
    example:
        from pyrainsty import mysql_connect
        config = dict(
            host='127.0.0.1',
            port='6379',
            password='123456',
            db='0'
        )

        rc = redis_connect.RedisConnect(config, decode_responses=True)
        rc.create_connect()
        result = rc.connect.get('key_name')
        print(result)

    """

    def __init__(self, _config, **_kwargs):
        self.__config = _config
        self.__kwargs = _kwargs
        self.__config['socket_connect_timeout'] = int(self.__config.get('socket_connect_timeout', 10))
        self.__checks = dict(mode=False if _config.get('mode', '0') == '0' else True)
        if 'mode' in self.__config.keys():
            del self.__config['mode']
        if 'expire' in self.__config.keys():
            del self.__config['expire']
        self.connect = None
        self.connect_pool = None

    def create_connect(self, identity=None):
        if not self.__checks['mode']:
            self.connect = self.get_conn_single()
        else:
            self.connect = self.get_conn_sentinel(identity)

    def get_conn(self):
        return self.connect

    def close_connect(self):
        try:
            if self.connect:
                self.connect = None
                self.connect_pool.disconnect()
            return True
        except (BaseException,):
            return False

    def __del__(self):
        self.close_connect()

    def get_conn_single(self):
        try:
            if self.alone_conn and self.alone_conn.ping():
                return self.alone_conn
            else:
                self._single()
                self._alone_conn()
                return self.alone_conn
        except (BaseException,):
            try:
                self._single()
                self._alone_conn()
                return self.alone_conn
            except BaseException as e:
                raise e

    def get_conn_sentinel(self, identity):
        if identity == 'master':
            try:
                if self.master_conn and self.master_conn.ping():
                    return self.master_conn
                else:
                    self._sentinel()
                    self._master_conn()
                    return self.master_conn
            except (BaseException,):
                try:
                    self._sentinel()
                    self._master_conn()
                    return self.master_conn
                except BaseException as e:
                    raise e

        elif identity == 'slave':
            try:
                if self.slave_conn and self.slave_conn.ping():
                    return self.slave_conn
                else:
                    self._sentinel()
                    self._slave_conn()
                    return self.slave_conn
            except (BaseException,):
                try:
                    self._sentinel()
                    self._slave_conn()
                    return self.slave_conn
                except BaseException as e:
                    raise e
        else:
            raise TypeError("Param <identity> Error, should be in ['master', 'slave]")

    def _single(self):
        self.__config['port'] = int(self.__config.get('port'))

    def _sentinel(self):
        hosts = self.__config.get('host').split(',')
        ports = self.__config.get('port').split(',')
        sentinel_servers = [(hosts[x], int(ports[x])) for x in range(len(hosts))]
        sentinel = Sentinel(sentinel_servers, socket_timeout=self.__config['socket_connect_timeout'])
        self.master = sentinel.discover_master('my_master')
        self.slave = sentinel.discover_slaves('my_slave')

    def _alone_conn(self):
        self.__config_alone = copy.deepcopy(self.__config)
        self.alone_pool = redis.ConnectionPool(**self.__config_alone, **self.__kwargs)
        self.alone_conn = redis.StrictRedis(connection_pool=self.alone_pool)
        self.connect_pool = self.alone_pool

    def _master_conn(self):
        self.__config_master = copy.deepcopy(self.__config)
        self.__config_master['host'] = self.master[0]
        self.__config_master['port'] = self.master[1]
        self.master_pool = redis.ConnectionPool(**self.__config_master, **self.__kwargs)
        self.master_conn = redis.Redis(connection_pool=self.master_pool)
        self.connect_pool = self.master_pool

    def _slave_conn(self):
        self.__config_slave = copy.deepcopy(self.__config)
        self.__config_slave['host'] = self.slave[0][0]
        self.__config_slave['port'] = self.slave[0][1]
        self.slave_pool = redis.ConnectionPool(**self.__config_slave, **self.__kwargs)
        self.slave_conn = redis.Redis(connection_pool=self.slave_pool)
        self.connect_pool = self.slave_pool
