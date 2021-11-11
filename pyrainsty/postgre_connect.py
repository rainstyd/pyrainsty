# -*- encoding: utf-8 -*-

"""
@author: rainsty
@file:   psycopg_connect.py
@time:   2021-11-09 19:51:26
@desc:   
"""

import psycopg2


class PostgreConnect(object):

    """
    example:
        from pyrainsty import postgre_connect
        config = dict(
            host='127.0.0.1',
            port='6538',
            user='test'
            password='123456',
            database='test'
        )

        pc = postgre_connect.PostgreConnect(config)
        pc.create_connect()
        result = pc.connect.get('select * from zzhq_zhijian.stock_nowinfo limit 1')
        print(result)
    """

    def __init__(self, _config, **kwargs):
        self.__config = _config
        self.__kwargs = kwargs
        self.__conn = None
        self.__cursor = None
        self.config = self.__config

    @property
    def get_conn(self):
        return self.__conn

    @property
    def get_cursor(self):
        return self.__cursor

    def create_connect(self):
        self.__conn = psycopg2.connect(**self.__config, **self.__kwargs)
        self.__cursor = self.__conn.cursor()

    def check_connect(self):
        try:
            if self.__conn.closed != 0:
                raise psycopg2.Error('The connect is closed.')
        except (BaseException,):
            self.create_connect()

    def close_connect(self):
        try:
            if self.__cursor:
                self.__cursor.close()
            if self.__conn:
                self.__conn.close()
            self.__cursor = None
            self.__conn = None
            return True
        except (BaseException,):
            return False

    def __del__(self):
        self.close_connect()

    def get_data(self, sql, params=None):
        try:
            self.check_connect()
            if params:
                self.__cursor.execute(sql, params)
            else:
                self.__cursor.execute(sql)

            _data = self.__cursor.fetchall()
            _column = self.__cursor.description

            _result = [dict(zip([column[0] for column in _column], data)) for data in _data]
            return _result
        except BaseException as _e:
            raise _e

    def exec_cmd(self, sql, params=None):
        try:
            self.check_connect()
            if params:
                self.__cursor.executemany(sql, params)
            else:
                self.__cursor.execute(sql)
            self.__conn.commit()
            return True
        except BaseException as _e:
            self.__conn.rollback()
            raise _e
