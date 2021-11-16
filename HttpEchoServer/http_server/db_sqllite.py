#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SQLLite query handler for Http file server."""

import sqlite3
import os
import json


class DBWorker:
    """Main class"""
    def __init__(self, db_name):
        self.db_conn = sqlite3.connect(os.getcwd() + db_name)
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

    def db_insert_update(self, attr_json) -> str:
        """Insert-update handler"""
        cur = self.db_conn.cursor()
        data = list(attr_json.values())
        try:
            cur.execute("INSERT INTO files VALUES(?, ?, ?, ?, ?, ?);", data)
            self.db_conn.commit()
            return 'OK'
        except sqlite3.Error as err:
            if str(err) == 'UNIQUE constraint failed: files.id':
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
            return result

    def search_name_from_id(self, attr_json) -> str:
        """Search file name in bd from file id"""
        cur = self.db_conn.cursor()
        try:
            cur.execute("SELECT name FROM files WHERE id = ?;",
                        (attr_json.get('id'),))
            searsh_result = cur.fetchone()
            self.db_conn.commit()

            if searsh_result:
                for row in searsh_result:
                    result = row
            else:
                result = False
            return result
        except sqlite3.Error as err:
            return err

    def get_metadata(self, query) -> json:
        """Create and execute query metadata"""
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
        cur.execute(query)
        searsh_result = cur.fetchall()
        self.db_conn.commit()

        metadata_result = []
        for i in searsh_result:
            result_json = {'id': i[0], 'name': i[1], 'tag': i[2], 'size': i[3],
                           'mimeType': i[4], 'modificationTime': i[5]}
            metadata_result.append(result_json)
        return metadata_result

    def get_file_data(self, query):
        """Get metadata from DB by query"""
        cur = self.db_conn.cursor()
        query = "SELECT name, size, mimeType FROM files WHERE id = '" + query + "'"
        cur.execute(query)
        searsh_result = cur.fetchone()
        self.db_conn.commit()
        return searsh_result

    def delete_file(self, file_id):
        """Delete file and metadata from storage and DB"""
        cur = self.db_conn.cursor()
        del_query = "DELETE FROM files WHERE id = '" + str(file_id) + "'"
        cur.execute(del_query)
        self.db_conn.commit()
