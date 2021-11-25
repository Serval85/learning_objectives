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
        logging.basicConfig(filename='log_db.log', filemode='w',
                            format='%(asctime)s %(name)s '
                                   '- %(levelname)s - '
                                   '%(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S',
                            level=logging.DEBUG)  # pylint: disable =  duplicate-code
        self.db_conn = sqlite3.connect(os.getcwd() + db_name)
        logging.info('Connect for db ' + str(os.getcwd() + db_name))
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
        logging.info('DB: ' + 'CREATE table files if not exits:')

    def db_insert_update(self, attr_json) -> str:
        """Insert-update handler"""
        cur = self.db_conn.cursor()
        data = list(attr_json.values())
        try:
            query = "INSERT INTO files VALUES(?, ?, ?, ?, ?, ?);"
            cur.execute(query, data)
            self.db_conn.commit()
            logging.debug('DB: db_insert_update: '
                          'try INSERT data if files: ' + data)
            logging.info('DB: db_insert_update: INSERT data for files' + data)
            return 'OK'
        except sqlite3.Error as err:
            if str(err) == 'UNIQUE constraint failed: files.id':
                logging.debug('DB: db_insert_update" '
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
            logging.debug('DB: db_insert_update: result' + result)
            return result

    def search_name_from_id(self, attr_json) -> str:
        """Search file name in bd from file id"""
        logging.debug('DB: search_name_from_id: attr_json:' + attr_json)
        cur = self.db_conn.cursor()
        try:
            cur.execute("SELECT name FROM files WHERE id = ?;",
                        (attr_json.get('id'),))
            search_result = cur.fetchone()
            self.db_conn.commit()
            logging.debug('DB: search_name_from_id: search_result:'
                          + search_result)

            if search_result:
                for row in search_result:
                    result = row
            else:
                result = False
            logging.debug('DB: search_name_from_id: result:' + result)
            return result
        except sqlite3.Error as err:
            logging.error('DB: search_name_from_id: ' + err)
            return err

    def get_metadata(self, query) -> json:
        """Create and execute query metadata"""
        logging.debug('DB: get_metadata: ' + query)
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
        logging.debug('DB: get_metadata: query: ' + query)
        cur.execute(query)
        search_result = cur.fetchall()
        self.db_conn.commit()

        metadata_result = []
        for i in search_result:
            result_json = {'id': i[0], 'name': i[1], 'tag': i[2], 'size': i[3],
                           'mimeType': i[4], 'modificationTime': i[5]}
            metadata_result.append(result_json)
        logging.info('DB: get_metadata: metadata_result: ' + metadata_result)
        return metadata_result

    def get_file_data(self, query):
        """Get metadata from DB by query"""
        logging.debug('DB: get_file_data: inn query:' + query)
        cur = self.db_conn.cursor()
        query = "SELECT name, size, mimeType FROM files WHERE id = '" +\
                query + "'"
        logging.debug('DB: get_file_data: sql query:' + query)
        cur.execute(query)
        search_file_result = cur.fetchone()
        self.db_conn.commit()
        logging.info('DB: get_file_data: search_file_result:' +
                     search_file_result)
        return search_file_result

    def delete_file(self, file_id):
        """Delete file and metadata from storage and DB"""
        logging.debug('DB: delete_file: inn file_id' + file_id)
        cur = self.db_conn.cursor()
        del_query = "DELETE FROM files WHERE id = '" + str(file_id) + "'"
        cur.execute(del_query)
        self.db_conn.commit()
        logging.info('DB: delete_file: deleted file_id' + file_id + 'from DB')
