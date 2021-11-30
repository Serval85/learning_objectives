#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SQLLite query handler for Http file server."""

import sqlite3
import os
import logging


class DBWorker:
    """Main class"""

    def __init__(self, db_name):
        logging.basicConfig(filename='log_db.log', filemode='w',
                            format='%(asctime)s %(name)s '
                                   '- %(levelname)s - '
                                   '%(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S',
                            level=logging.DEBUG)  # pylint: disable =
        # duplicate-code
        self.db_conn = sqlite3.connect(os.getcwd() + db_name,
                                       detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
        logging.info('Connect for db ' + str(os.getcwd() + db_name))
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
        logging.info('DB: ' + 'CREATE tables first_coin_date,'
                              'bpi if not exits:')
        return 'Db created'

    def db_insert(self, table_name, data_pack):
        """Insert handler"""

        logging.debug('DB: db_insert: in ' + table_name +
                      ' , data_pack:' + str(data_pack))
        query = 'INSERT OR IGNORE INTO ' + table_name + '(date, price) ' \
                                                        'VALUES(?,?) '
        cur = self.db_conn.cursor()
        cur.executemany(query, data_pack.items())
        self.db_conn.commit()
        logging.info('DB: db_insert: in ' + table_name +
                     ' , data_pack:' + str(data_pack))
        return 'data_pack inserted in db'

    def get_data(self, table_name, start_date, end_date):
        """Get exiting data from DB"""
        query = 'SELECT * FROM ' + table_name + ' WHERE date BETWEEN "' + \
                start_date + '" AND "' + end_date + '"'
        logging.info('DB: get_data: from ' + table_name +
                     ' , query:' + str(query))
        cur = self.db_conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        self.db_conn.commit()
        logging.debug('DB: get_data: from ' + table_name +
                      ', result:' + str(result))
        return result

    def db_insert_first_date(self, coin_name, date) -> str:
        """Insert handler"""
        query = 'INSERT OR IGNORE INTO first_coin_date(coin_name, date) ' \
                'VALUES(?,?) '
        cur = self.db_conn.cursor()
        cur.execute(query, (coin_name, date))
        self.db_conn.commit()
        logging.info('DB: db_insert_first_date: ' 'first date= ' + str(date)
                     + ' for ' + coin_name + ' inserted in db')
        return date

    def get_first_date(self, coin_name):
        """Get exiting data from DB"""
        query = 'SELECT date FROM first_coin_date WHERE coin_name="' \
                + coin_name + '"'
        cur = self.db_conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        self.db_conn.commit()
        logging.debug('DB: get_first_date: result: ' + str(result))
        if result:
            return str(result[0])
        else:
            return None
