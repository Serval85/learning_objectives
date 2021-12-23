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
        log.info('Response headers for send: %s', str(self.headers))

        if response_pack.get('write_message'):
            send_message = bytes(response_pack.get('write_message'))
        else:
            send_message = bytes(response_pack.get('status'))
        self.wfile.write(send_message)

    def do_POST(self):  # pylint: disable = invalid-name
        """Post handler"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            mime_type = self.headers.get('Content-Type',
                                         'application/octet-stream')
            modification_time = str(datetime.datetime.now())

            log.debug('do_POST: content_length: %s / '
                      'mime_type: %s / '
                      'modification_time: %s',
                      str(content_length),
                      str(mime_type),
                      str(modification_time))

            if content_length < 1:
                response_pack = {'status': 400, 'message': 'Bad Request',
                                 'write_message':
                                     bytes("Gde den'gi, Lebovski?", 'UTF-8'),
                                 'content_length': '', 'content_type': ''}
                self.api_send_response(response_pack)
                log.debug('do_POST: Response_pack: %s', str(response_pack))
                return
            send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
            if send_uri == '/api/upload':
                query = parse_qs(
                    urlparse(self.path, scheme='', allow_fragments=True).query)
                log.debug('do_POST: /api/upload query: %s', str(query))
                try:
                    file_id = query.get('id', None)
                    if file_id is None:
                        file_id = uuid.uuid4()
                    else:
                        file_id = file_id[0]
                except TypeError('NoneType'):
                    file_id = uuid.uuid4()

                file_name = str(query.get('name', [file_id])[0])
                file_tag = query.get('tag', ['None'])[0]

                attr_json = {'id': str(file_id), 'name': file_name,
                             'tag': file_tag, 'size': content_length,
                             'mimeType': mime_type,
                             'modificationTime': modification_time}
                payload = self.rfile.read(content_length)

                result_search_id = dbw.search_name_from_id(attr_json)
                log.debug('do_POST: Result_search_id: %s',
                          str(result_search_id))

                if result_search_id and \
                        os.path.isfile(str(result_search_id[0])):
                    os.remove(str(result_search_id[0]))

                result_db_insert = dbw.db_insert_update(attr_json)
                log.debug('do_POST: Result_db_insert: %s',
                          str(result_db_insert))

                if result_db_insert in ['OK', 'UPDATE']:
                    try:
                        with open(str(file_id), 'wb') as file:
                            file.write(payload)
                    finally:
                        log.error('do_POST: write file: %s', str(file_id))
                        # file.close()

                    response_pack = {'status': 201, 'message': 'Created',
                                     'write_message':
                                         bytes(json.dumps(attr_json), 'UTF-8'),
                                     'content_length': '', 'content_type': ''}
                else:
                    response_pack = {'status': 500,
                                     'message': 'Internal Server Error',
                                     'write_message': '',
                                     'content_length': '', 'content_type': ''}

                log.debug('do_POST: Response_pack: %s', str(response_pack))
                self.api_send_response(response_pack)
        except MemoryError:
            response_pack = {'status': 418,
                             'message': 'I’m a teapot',
                             'write_message':
                                 bytes('A harya ne tresnet?', 'UTF-8'),
                             'content_length': '', 'content_type': ''}
            self.api_send_response(response_pack)
            log.error('do_POST: %s error on post', str(MemoryError))
            return

    def do_GET(self):  # pylint: disable = invalid-name
        """Get handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        log.debug('do_GET: %s', send_uri)
        if send_uri == '/api/get':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            log.debug('do_GET: query: %s', str(query))
            response_message = json.dumps(dbw.get_metadata(query))
            response_pack = {'status': 200,
                             'message': 'OK',
                             'write_message': bytes(response_message, 'UTF-8'),
                             'content_length':
                                 len(bytes(response_message, 'UTF-8')),
                             'content_type': ''}
            self.api_send_response(response_pack)
        elif send_uri == '/api/download':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            log.debug('do_GET: %s', send_uri)
            file_data = dbw.get_file_data(query.get('id')[0])
            if file_data:
                log.debug('do_GET: file_data: %s', str(file_data))
                file_name = file_data[0]
                file_size = file_data[1]
                file_type = file_data[2]
                try:
                    with open(query.get('id')[0], 'rb') as file:
                        response_message = file.read()
                        file.close()
                finally:
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
            log.debug('do_GET: response: %s', str(response_pack.get('status')))
            self.api_send_response(response_pack)

    def do_DELETE(self):  # pylint: disable = invalid-name
        """Delete handler"""
        send_uri = urlparse(self.path, scheme='', allow_fragments=True).path
        log.debug('do_DELETE: send_uri: %s', str(send_uri))
        if send_uri == '/api/delete':
            query = parse_qs(
                urlparse(self.path, scheme='', allow_fragments=True).query)
            log.debug('do_DELETE: query: %s', str(query))
            if query:
                file_data = dbw.get_metadata(query)
                deleted = 0
                for i in file_data:
                    result_search_name = \
                        dbw.search_name_from_id(i)
                    log.debug('do_DELETE: result_search_name: %s',
                                  str(result_search_name[0]))

                    # deleted = 0
                    if result_search_name[0] and\
                            os.path.isfile(str(result_search_name[0])):
                        os.remove(str(result_search_name[0]))
                        log.info('do_DELETE: %s - deleted',
                                 str(result_search_name[1]))
                        deleted += 1
                        dbw.delete_file(i.get('id'))

                message = str(deleted) + ' files deleted'
                log.info('do_DELETE: message for delete: %s', message)
                self.send_response(200, message)
                self.end_headers()
            else:
                log.info('do_DELETE: No parameters')
                self.send_response(400, 'No parameters')
                self.end_headers()


def main():
    """Main func. Start http server"""
    server = HTTPServer(('127.0.0.1', 10001), RequestHandler)
    log.info('Start http_server. IP: %s, DB name %s, DB name:',
             str(server.server_address), DB_NAME)
    server.serve_forever()


if __name__ == "__main__":
    log = logging.getLogger('http_server')
    log.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("log.log")
    formatter = logging.Formatter('%(asctime)s %(name)s - %(levelname)s - '
                                  '%(message)s')
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    main()
