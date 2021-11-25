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
from db_sqllite import DBWorker  # pylint: disable = import-error

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
        if response_pack.get('Content-Disposition'):
            self.send_header("Content-Disposition",
                             response_pack.get('Content-Disposition'))
        self.end_headers()
        logging.info('Response headers for send: ' + str(self.headers))
        self.wfile.write(response_pack.get('write_message'))

    def do_POST(self):  # pylint: disable = invalid-name
        """Post handler"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            mime_type = self.headers.get('Content-Type',
                                         'application/octet-stream')
            modification_time = str(datetime.datetime.now())

            logging.debug('do_POST: content_length:' + str(content_length) +
                          ' / ' + 'mime_type:' + str(mime_type) +
                          ' / ' + 'modification_time:' + str(modification_time))

            if content_length < 1:
                response_pack = {'status': 400, 'message': 'Bad Request',
                                 'write_message':
                                     bytes("Gde den'gi, Lebovski?", 'UTF-8'),
                                 'content_length': '', 'content_type': ''}
                self.api_send_response(response_pack)
                logging.debug('do_POST: Response_pack:' + str(response_pack))
                return
            send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
            if send_uri == '/api/upload':
                query = parse_qs(
                    urlparse(self.path, scheme='', allow_fragments=True).query)
                logging.debug('do_POST: /api/upload query:' + str(query))
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
                logging.debug('do_POST: Result_search_id:' +
                              str(result_search_id))

                if result_search_id and os.path.isfile(result_search_id):
                    os.remove(result_search_id)

                result_db_insert = dbw.db_insert_update(attr_json)
                logging.debug('do_POST: Result_db_insert:' +
                              str(result_db_insert))

                if result_db_insert in ['OK', 'UPDATE']:
                    try:
                        with open(file_id, 'wb') as file:
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

                logging.debug('do_POST: Response_pack:' + str(response_pack))
                self.api_send_response(response_pack)
        except MemoryError:
            response_pack = {'status': 418,
                             'message': 'I’m a teapot',
                             'write_message':
                                 bytes('A harya ne tresnet?', 'UTF-8'),
                             'content_length': '', 'content_type': ''}
            self.api_send_response(response_pack)
            logging.error('do_POST: ' + MemoryError + ' error on post')
            return

    def do_GET(self):  # pylint: disable = invalid-name
        """Get handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        logging.debug('do_GET: ' + send_uri)
        if send_uri == '/api/get':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            logging.debug('do_GET: query: ' + str(query))
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
            logging.debug('do_GET: ' + send_uri)
            file_data = dbw.get_file_data(query.get('id')[0])
            if file_data:
                logging.debug('do_GET: file_data: ' + str(file_data))
                file_name = file_data[0]
                file_size = file_data[1]
                file_type = file_data[2]
                with open(query.get('id')[0], 'rb') as file:
                    response_message = file.read()
                    file.close()
                response_pack = {'status': 200,
                                 'message': 'OK',
                                 'write_message': response_message,
                                 'content_length': file_size,
                                 'content_type': file_type,
                                 'content-disposition': file_name}
            else:
                response_pack = {'status': 404,
                                 'message': 'Not found',
                                 'write_message': '',
                                 'content_length': '',
                                 'content_type': ''}
            logging.debug('do_GET: response_pack: ' + str(response_pack))
            self.api_send_response(response_pack)

    def do_DELETE(self):  # pylint: disable = invalid-name
        """Delete handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        logging.debug('do_DELETE: send_uri: ' + str(send_uri))
        if send_uri == '/api/delete':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            logging.debug('do_DELETE: query: ' + str(query))
            if query:
                file_data = dbw.get_metadata(query)
                for i in file_data:
                    result_search_name = dbw.search_name_from_id(i)
                    logging.debug('do_DELETE: result_search_name: ' +
                                  str(result_search_name))

                    deleted = 0
                    if result_search_name and os.path.isfile(result_search_name):
                        os.remove(result_search_name)
                        logging.info('do_DELETE: ' + str(result_search_name) +
                                      ' - deleted')
                        deleted += 1
                        dbw.delete_file(i.get('id'))

                message = str(deleted) + ' files deleted'
                logging.info('do_DELETE: message for delete:' + message)
                self.send_response(200, message)
                self.end_headers()
            else:
                logging.info('do_DELETE: No parameters')
                self.send_response(400, 'No parameters')
                self.end_headers()


if __name__ == "__main__":
    logging.basicConfig(filename='log.log', filemode='w',
                        format='%(asctime)s %(name)s '
                               '- %(levelname)s - '
                               '%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        level=logging.DEBUG)  # pylint: disable = duplicate-code

    server = HTTPServer(('127.0.0.1', 10001), RequestHandler)
    logging.info('Start http_server. IP: '  # pylint: disable = logging-not-lazy
                 + str(server.server_address) +
                 ', DB name:' + DB_NAME)
    server.serve_forever()
