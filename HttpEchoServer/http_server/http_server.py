# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""Http file server.
For storage any files and metadata"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime
import os
import json
import uuid
import logging
from http_server.db_sqllite import DBWorker

DB_NAME = r'/db/metadata.db'
dbw = DBWorker(DB_NAME)


class RequestHandler(BaseHTTPRequestHandler):
    """Class  HTTPRequestHandler. Process http requests"""
    def api_send_response(self, response_pack):
        """Common method for send response"""

        self.send_response(response_pack.get('status'),
                           response_pack.get('message'))
        if response_pack.get('content_length'):
            self.send_header("Content-Length",
                             response_pack.get('content_length'))
        else:
            self.send_header("Content-Length",
                             len(response_pack.get('write_message')))
        if response_pack.get('content_type'):
            self.send_header("Content-Type",
                             response_pack.get('content_type'))
        self.end_headers()
        self.wfile.write(response_pack.get('write_message'))

    def do_POST(self):  # pylint: disable = invalid-name
        """Post handler"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            mime_type = self.headers.get('Content-Type',
                                         'application/octet-stream')
            modification_time = str(datetime.datetime.now())

            if content_length < 1:
                response_pack = {'status': 400, 'message': 'Bad Request',
                                 'write_message':
                                     bytes("Gde den'gi, Lebovski?", 'UTF-8'),
                                 'content_length': '', 'content_type': ''}
                self.api_send_response(response_pack)
                return
            send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
            if send_uri == '/api/upload':
                query = parse_qs(
                    urlparse(self.path, scheme='', allow_fragments=True).query)
                try:
                    file_id = query.get('id', None)
                    if file_id is None:
                        file_id = uuid.uuid4()
                    else:
                        file_id = file_id[0]
                except TypeError('NoneType'):
                    file_id = uuid.uuid4()

                file_name = query.get('name', [file_id])[0]
                file_tag = query.get('tag', ['None'])[0]

                attr_json = {'id': file_id, 'name': file_name, 'tag': file_tag,
                             'size': content_length, 'mimeType': mime_type,
                             'modificationTime': modification_time}
                payload = self.rfile.read(content_length)

                result_search_id = dbw.search_name_from_id(attr_json)

                if result_search_id and os.path.isfile(result_search_id):
                    os.remove(result_search_id)

                result_db_insert = dbw.db_insert_update(attr_json)

                if result_db_insert in ['OK', 'UPDATE']:
                    try:
                        with open(file_name, 'wb') as file:
                            file.write(payload)
                    finally:
                        file.close()

                    response_pack = {'status': 201, 'message': 'Created',
                                     'write_message':
                                         bytes(json.dumps(attr_json), 'UTF-8'),
                                     'content_length': '', 'content_type': ''}
                else:
                    response_pack = {'status': 500,
                                     'message': 'Internal Server Error',
                                     'write_message': '',
                                     'content_length': '', 'content_type': ''}
                self.api_send_response(response_pack)
        except MemoryError:
            response_pack = {'status': 418,
                             'message': 'I’m a teapot',
                             'write_message':
                                 bytes('A harya ne tresnet?', 'UTF-8'),
                             'content_length': '', 'content_type': ''}
            self.api_send_response(response_pack)
            return

    def do_GET(self):  # pylint: disable = invalid-name
        """Get handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        if send_uri == '/api/get':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            response_message = str(dbw.get_metadata(query))
            response_pack = {'status': 200,
                             'message': 'OK',
                             'write_message': bytes(response_message, 'UTF-8'),
                             'content_length':
                                 len(bytes(response_message, 'UTF-8')),
                             'content_type': ''}
        elif send_uri == '/api/download':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            file_data = dbw.get_file_data(query.get('id')[0])
            if file_data:
                file_name = file_data[0]
                file_size = file_data[1]
                file_type = file_data[2]
                with open(file_name, 'rb') as file:
                    response_message = file.read()
                    file.close()
                response_pack = {'status': 200,
                                 'message': 'OK',
                                 'write_message': response_message,
                                 'content_length': file_size,
                                 'content_type': file_type}
            else:
                response_pack = {'status': 404,
                                 'message': 'Not found',
                                 'write_message': '',
                                 'content_length': '',
                                 'content_type': ''}
        self.api_send_response(response_pack)

    def do_DELETE(self):  # pylint: disable = invalid-name
        """Delete handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        if send_uri == '/api/delete':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            if query:
                file_data = dbw.get_metadata(query)
                for i in file_data:
                    result_search_name = dbw.search_name_from_id(i)

                    deleted = 0
                    if result_search_name and os.path.isfile(result_search_name):
                        print(result_search_name + ' - deleted')
                        os.remove(result_search_name)
                        deleted += 1
                        dbw.delete_file(i.get('id'))

                message = str(deleted) + ' files deleted'
                self.send_response(200, message)
                self.end_headers()
            else:
                self.send_response(400, 'No parameters')
                self.end_headers()


if __name__ == "__main__":
    logging.basicConfig(filename='log.log', filemode='w',
                        format='%(asctime)s %(name)s '
                               '- %(levelname)s - '
                               '%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        level=logging.DEBUG)

    server = HTTPServer(('127.0.0.1', 10001), RequestHandler)
    logging.info('Start http_server. IP: '  # pylint: disable = logging-not-lazy
                 + str(server.server_address) +
                 ', DB name:' + DB_NAME)
    server.serve_forever()
