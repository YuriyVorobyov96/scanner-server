import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

class Utilities:
    @staticmethod
    def do_ping_sweep(ip, num_of_hosts):
        result = ''

        for host_num in range(num_of_hosts): 
            result += Utilities.__do_ping(ip, host_num)

        return result

    @staticmethod
    def sent_http_request(target, method, headers, payload):
        if method.upper() == 'GET':
            response = requests.get(target, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(target, headers=headers, data=payload)

        return f'[#] Response status code: {response.status_code}\n' +\
            f'[#] Response headers: {json.dumps(dict(response.headers), indent=4, sort_keys=True)}\n' +\
            f'[#] Response content:\n {response.text}'

    @staticmethod
    def __do_ping(ip, host_num):
        ip_parts = ip.split('.')
        network_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
        scanned_ip = network_ip + str(int(ip_parts[3]) + host_num)

        response = os.popen(f'ping -c 1 {scanned_ip}')
        res = response.readlines()

        return f'[#] Result of scanning: {scanned_ip} [#]\n{res[3]}\n\n'


class WebRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/scan':
            try:
                self.__check_json_request_content_type()
            except Exception as err:
                return self.__send_bad_request_error(err)

            data = self.__get_request_body()

            try:
                self.__validate_scan_request_body(data)
            except Exception as err:
                return self.__send_bad_request_error(err)

            try:
                result = Utilities.do_ping_sweep(data['target'], int(data['count']))
                return self.__send_result(result)
            except Exception as err:
                return self.__send_internal_server_error(err)

        return self.__send_not_found_error()

    def do_POST(self):
        if self.path == '/sendhttp':
            try:
                self.__check_json_request_content_type()
            except Exception as err:
                return self.__send_bad_request_error(err)

            data = self.__get_request_body()

            try:
                self.__validate_sent_http_request_request_body(data)
            except Exception as err:
                return self.__send_bad_request_error(err)

            try:
                result = Utilities.sent_http_request(data['target'], data['method'], data.get('headers', dict()), data.get('payload', None))
                return self.__send_result(result)
            except Exception as err:
                return self.__send_internal_server_error(err)

        return self.__send_not_found_error()

    def __do_response(self, status_code=200, content=''):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        response = bytes(f'{content}', 'utf8')
        self.wfile.write(response)

    def __send_not_found_error(self):
        self.__do_response(404, 'Invalid path')

    def __send_bad_request_error(self, err):
        self.__do_response(400, err)

    def __send_internal_server_error(self, err):
        print(err)
        self.__do_response(500, 'Internal server error')

    def __send_result(self, result):
        self.__do_response(200, result)

    def __get_content_type_header(self):
        return self.headers.get('Content-Type')

    def __get_request_body(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)

        body = json.loads(post_body)

        return { k.lower(): v for k, v in body.items() }

    def __is_json_content_type(self, content_type):
        return content_type == 'application/json'
    
    def __check_json_request_content_type(self):
        content_type = self.__get_content_type_header()

        if not self.__is_json_content_type(content_type):
            raise Exception('Invalid Header Type')

    def __validate_scan_request_body(self, data):
        if not 'target' in data and not 'count' in data:
            raise Exception('Missed "target" and "count" params')
        if not 'target' in data:
            raise Exception('Missed "target" param')
        if not 'count' in data:
            raise Exception('Missed "count" param')

    def __validate_sent_http_request_request_body(self, data):
        if not 'target' in data and not 'method' in data:
            raise Exception('Missed "target" and "method" params')
        if not 'target' in data:
            raise Exception('Missed "target" param')
        if not 'method' in data:
            raise Exception('Missed "method" param')
        method = data['method'].upper()
        if not (method == 'GET' or method == 'POST'):
            raise Exception(f'Unsupported method "{method}"')
        headers = data.get('headers', None)
        if headers:
            if not (type(headers) == dict):
                raise Exception('Invalid headers format')
        payload = data.get('payload', None)
        if  payload:
            if not (type(payload) == dict):
                raise Exception('Invalid payload format')


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler, host='0.0.0.0', port=3000):
    print(f'Server started at port {port}. Press CTRL+C to close the server.')
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Server Closed')

run(socketserver.TCPServer, WebRequestHandler)