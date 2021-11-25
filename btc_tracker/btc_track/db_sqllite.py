#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SQLLite query handler for Http file server."""

import sqlite3
import os
import json


class DBWorker:
    """Main class"""
    def __init__(self, db_name):
        self.db_conn = sqlite3.connect(os.getcwd() + db_name,
                                       detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
        self.db_table_create()

    def db_table_create(self):
        """Create main tables for metadata"""
        cur = self.db_conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS '
                    'first_coin_date(date DATE PRIMARY KEY, coin_name REAL);')
        self.db_conn.commit()

        cur.execute('CREATE TABLE IF NOT EXISTS '
                    'bpi(date DATE PRIMARY KEY, price REAL);')
        self.db_conn.commit()
        return 'Db created'

    def db_insert(self, table_name, data_pack):
        """Insert handler"""
        print('data_pack = ', data_pack)
        query = 'INSERT OR IGNORE INTO ' + table_name + '(date, price) ' \
                                                        'VALUES(?,?) '
        cur = self.db_conn.cursor()
        cur.executemany(query, data_pack.items())
        self.db_conn.commit()
        print('data_pack inserted in db')
        return 'data_pack inserted in db'

    def get_data(self, table_name, start_date, end_date):
        """Get exiting data from DB"""
        query = 'SELECT * FROM ' + table_name + ' WHERE date BETWEEN "' +\
                start_date + '" AND "' + end_date + '"'
        print(query)
        cur = self.db_conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        self.db_conn.commit()
        return result

    def db_insert_first_date(self, coin_name, date) -> str:
        """Insert handler"""
        query = 'INSERT OR IGNORE INTO first_coin_date(coin_name, date) VALUES(?,?)'
        cur = self.db_conn.cursor()
        cur.execute(query, (coin_name, date))
        self.db_conn.commit()
        return 'First date= ' + str(date) + ' for ' + coin_name + \
               ' inserted in db'

    def get_first_date(self, coin_name):
        """Get exiting data from DB"""
        query = 'SELECT date FROM first_coin_date WHERE coin_name="'\
                + coin_name + '"'
        cur = self.db_conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        self.db_conn.commit()
        if result:
            return str(result[0])
        else:
            return None
