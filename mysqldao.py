# -*- coding: utf-8 -*-


import MySQLdb
from config import Config
from time import sleep
import sys


class MysqlDao():
    _mysql = {}

    def __init__(self):
        self._init_mysql()

    def _init_mysql(self):
        n = 0
        while True:
            try:
                self._mysql["conn"] = MySQLdb.connect(host=Config.mysql_host, user=Config.mysql_user,
                                                      passwd=Config.mysql_password,
                                                      db=Config.mysql_dbname, port=Config.mysql_port,
                                                      charset=Config.mysql_charset)
                self._mysql["cur"] = self._mysql["conn"].cursor()
                break
            except Exception, e:
                print Exception, ":", e
                if n >= Config.mysql_retry_times:
                    print ('Mysql Connect Error,exit!')
                    sys.exit()
                else:
                    n = n + 1
                    print ('Mysql Connect Error,sleep!')
                    sleep(100)

    def _close_mysql(self):
        if self._mysql:
            try:
                self._mysql["conn"].close()
                self._mysql["cur"].close()
            except MySQLdb.Error, e:
                print e
                sys.exit()

    def execute(self, sql):
        try:
            self._mysql["conn"].ping()
        except:
            self._init_mysql()

        self._mysql["cur"].execute(sql)
        self._mysql["conn"].commit()
