# -*- coding: utf-8 -*-
# !/usr/bin/env python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import random
import datetime
import sqlite3
import os
import json


class RequestHandler(BaseHTTPRequestHandler):
    def api_send_response(self, status, message, write_message, content_length, content_type):
        self.send_response(status, message)
        if content_length:
            self.send_header("Content-Length", content_length)
        else:
            self.send_header("Content-Length", len(write_message))
        if content_type:
            self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(write_message)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            mime_type = self.headers.get('Content-Type', 'application/octet-stream')
            modification_time = str(datetime.datetime.now())

            if content_length < 1:
                self.api_send_response(400, 'Bad Request', bytes("Gde den'gi, Lebovski?", 'UTF-8'), '', '')
                return
            send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
            if send_uri == '/api/upload':
                query = parse_qs(urlparse(self.path, scheme='', allow_fragments=True).query)
                try:
                    file_id = query.get('id', None)
                    if file_id is None:
                        file_id = (['%032x' % random.getrandbits(128)])[0]
                    else:
                        file_id = file_id[0]
                except TypeError('NoneType'):
                    file_id = (['%032x' % random.getrandbits(128)])[0]

                file_name = query.get('name', [file_id])[0]
                file_tag = query.get('tag', ['None'])[0]

                attr_json = {'id': file_id, 'name': file_name, 'tag': file_tag,
                             'size': content_length, 'mimeType': mime_type, 'modificationTime': modification_time}
                payload = self.rfile.read(content_length)

                result_search_id = search_name_from_id(attr_json)

                if result_search_id and os.path.isfile(result_search_id):
                    os.remove(result_search_id)

                result_db_insert = db_insert_update(attr_json)
                if result_db_insert in ['OK', 'UPDATE']:
                    try:
                        file = open(file_name, "wb")
                        file.write(payload)
                    finally:
                        file.close()
                    self.api_send_response(201, 'Created', bytes(json.dumps(attr_json), 'UTF-8'), '', '')
                else:
                    self.api_send_response(500, 'Internal Server Error', '', '', '')
        except MemoryError:
            self.api_send_response(418, 'I’m a teapot', bytes('A harya ne tresnet?', 'UTF-8'), '', '')
            return

    def do_GET(self):
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        if send_uri == '/api/get':
            query = parse_qs(urlparse(self.path, scheme='', allow_fragments=True).query)
            response_message = str(get_metadata(query))
            self.api_send_response(200, 'OK', bytes(response_message, 'UTF-8'), len(bytes(response_message, 'UTF-8')), '')
        elif send_uri == '/api/download':
            query = parse_qs(urlparse(self.path, scheme='', allow_fragments=True).query)
            file_data = get_file_data(query.get('id')[0])
            if file_data:
                file_name = file_data[0]
                file_size = file_data[1]
                file_type = file_data[2]
                file = open(file_name, "rb")
                response_message = file.read()
                file.close()
                self.api_send_response(200, 'OK', response_message, file_size, file_type)
            else:
                self.api_send_response(404, 'Not found', '', '', '')

    def do_DELETE(self):
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        if send_uri == '/api/delete':
            query = parse_qs(urlparse(self.path, scheme='', allow_fragments=True).query)
            if query:
                file_data = get_metadata(query)
                deleted = 0
                for i in file_data:
                    print(i.get('id'))
                    result_search_name = search_name_from_id(i)

                    if result_search_name and os.path.isfile(result_search_name):
                        print(result_search_name + ' - deleted')
                        os.remove(result_search_name)
                        deleted += 1
                        del_query = "DELETE FROM files WHERE id = '" + str(i.get('id')) + "'"
                        cur.execute(del_query)
                        conn.commit()

                message = str(deleted) + ' files deleted'
                self.send_response(200, message)
                self.end_headers()
            else:
                self.send_response(400, 'No parameters')
                self.end_headers()


def db_table_create():
    cur.execute("""CREATE TABLE IF NOT EXISTS files(
       id INT PRIMARY KEY,
       name TEXT,
       tag TEXT,
       size INT,
       mimeType TEXT,
       modificationTime TEXT);
    """)
    conn.commit()


def db_insert_update(attr_json):
    data = list(attr_json.values())
    try:
        # print(data)
        cur.execute("INSERT INTO files VALUES(?, ?, ?, ?, ?, ?);", data)
        conn.commit()
        return 'OK'
    except sqlite3.Error as err:
        if str(err) == 'UNIQUE constraint failed: files.id':
            data_buf = data[0]
            data = data[1:]
            data.append(data_buf)
            # print(data)
            cur.execute("""UPDATE files
                        SET name = ?, tag = ?, size = ?, mimeType = ?, modificationTime = ? 
                        WHERE id = ?;""", data)
            return 'UPDATE'
        else:
            return err


def search_name_from_id(attr_json):
    try:
        cur.execute("SELECT name FROM files WHERE id = ?;", (attr_json.get('id'), ))
        searsh_result = cur.fetchone()
        conn.commit()

        if searsh_result:
            for row in searsh_result:
                result = row
            return result
        else:
            return False
    except sqlite3.Error as err:
        return err


def get_metadata(query):
    query_str = ''
    for i in query.keys():
        k = 0
        for j in query.get(i):
            query_str += str(i) + " = '" + str(query.get(i)[k]) + "' or "
            k += 1
        query_str = query_str[:-4]
        query_str += ' and '
    if len(query_str):
        query_str = ' WHERE ' + query_str[:-5]
    else:
        query_str = ''
    query = "SELECT * FROM files" + query_str
    cur.execute(query)
    searsh_result = cur.fetchall()
    conn.commit()

    metadata_result = []
    for i in searsh_result:
        result_json = {'id': i[0], 'name': i[1], 'tag': i[2], 'size': i[3], 'mimeType': i[4], 'modificationTime': i[5]}
        metadata_result.append(result_json)
    return metadata_result


def get_file_data(query):
    query = "SELECT name, size, mimeType FROM files WHERE id = '" + query + "'"
    cur.execute(query)
    searsh_result = cur.fetchone()
    conn.commit()
    return searsh_result


if __name__ == "__main__":
    conn = sqlite3.connect(os.getcwd() + r'/db/metadata.db')
    cur = conn.cursor()
    db_table_create()
    server = HTTPServer(('127.0.0.1', 10001), RequestHandler)
    server.serve_forever()
    conn.close()
