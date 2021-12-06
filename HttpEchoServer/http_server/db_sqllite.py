#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SQLLite query handler for Http file server."""

import sqlite3
import os
import json
import logging


class DBWorker:
    """Main class"""
    def __init__(self, db_name):
        self.db_log = logging.getLogger('db_sqllite')
        self.db_log.setLevel(logging.DEBUG)
        db_file_handler = logging.FileHandler("log.log")
        formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - '
                                      '%(message)s')
        db_file_handler.setFormatter(formatter)
        self.db_log.addHandler(db_file_handler)

        self.db_conn = sqlite3.connect(os.getcwd() + db_name)
        self.db_log.info('Connect for db %s', str(os.getcwd() + db_name))
        self.db_table_create()

    def db_table_create(self):
        """Create main table for metadata"""
        cur = self.db_conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS files(
           id INT PRIMARY KEY,
           name TEXT,
           tag TEXT,
           size INT,
           mimeType TEXT,
           modificationTime TEXT);
        """)
        self.db_conn.commit()
        self.db_log.info('CREATE table files if not exits:')

    def db_insert_update(self, attr_json) -> str:
        """Insert-update handler"""
        cur = self.db_conn.cursor()
        data = list(attr_json.values())
        try:
            query = "INSERT INTO files VALUES(?, ?, ?, ?, ?, ?);"
            cur.execute(query, data)
            self.db_conn.commit()

            self.db_log.debug('db_insert_update: try INSERT data if files: %s',
                              str(data))
            return 'OK'
        except sqlite3.Error as err:
            if str(err) == 'UNIQUE constraint failed: files.id':
                self.db_log.debug('db_insert_update" '
                                  'UNIQUE constraint failed: files.id: Update')

                data_buf = data[0]
                data = data[1:]
                data.append(data_buf)
                cur.execute("""UPDATE files
                            SET name = ?, tag = ?, size = ?, mimeType = ?, 
                            modificationTime = ? 
                            WHERE id = ?;""", data)
                result = 'UPDATE'
            else:
                result = err
            self.db_log.debug('db_insert_update: result %s', result)
            return result

    def search_name_from_id(self, attr_json):
        """Search file name in bd from file id"""
        self.db_log.debug('search_name_from_id: attr_json: %s', str(attr_json))
        cur = self.db_conn.cursor()
        try:
            cur.execute("SELECT * FROM files WHERE id = ?;",
                        (attr_json.get('id'),))
            search_result = cur.fetchone()
            self.db_conn.commit()
            self.db_log.debug('search_name_from_id: search_result: %s',
                              str(search_result))

            if search_result:
                result_id = search_result[0]
                result_name = search_result[1]
                result = [result_id, result_name]
            else:
                return False
            self.db_log.debug('search_name_from_id: result: %s', str(result))
            return result
        except sqlite3.Error as err:
            self.db_log.error('search_name_from_id: %s', str(err))
            return False

    def get_metadata(self, query) -> json:
        """Create and execute query metadata"""
        self.db_log.debug('get_metadata: %s', str(query))
        cur = self.db_conn.cursor()
        query_str = ''
        for i in query.keys():
            k = 0
            for _ in query.get(i):
                query_str += str(i) + " = '" + str(query.get(i)[k]) + "' or "
                k += 1
            query_str = query_str[:-4]
            query_str += ' and '
        if len(query_str) > 0:
            query_str = ' WHERE ' + query_str[:-5]
        else:
            query_str = ''
        query = "SELECT * FROM files" + query_str
        self.db_log.debug('get_metadata: query: %s', query)
        cur.execute(query)
        search_result = cur.fetchall()
        self.db_conn.commit()

        metadata_result = []
        for i in search_result:
            result_json = {'id': i[0], 'name': i[1], 'tag': i[2], 'size': i[3],
                           'mimeType': i[4], 'modificationTime': i[5]}
            metadata_result.append(result_json)
        self.db_log.info('get_metadata: metadata_result: %s',
                         str(metadata_result))
        return metadata_result

    def get_file_data(self, query):
        """Get metadata from DB by query"""
        self.db_log.debug('get_file_data: inn query: %s', query)
        cur = self.db_conn.cursor()
        query = "SELECT name, size, mimeType FROM files WHERE id = '" +\
                query + "'"
        self.db_log.debug('get_file_data: sql query: %s', query)
        cur.execute(query)
        search_file_result = cur.fetchone()
        self.db_conn.commit()
        self.db_log.info('get_file_data: search_file_result: %s',
                         str(search_file_result))
        return search_file_result

    def delete_file(self, file_id):
        """Delete file and metadata from storage and DB"""
        self.db_log.debug('delete_file: inn file_id %s', file_id)
        cur = self.db_conn.cursor()
        del_query = "DELETE FROM files WHERE id = '" + str(file_id) + "'"
        cur.execute(del_query)
        self.db_conn.commit()
        self.db_log.info('delete_file: deleted file_id %s from DB', file_id)
