#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

HTTP_VERSION_KEY = "Http-version"
STATUS_CODE_KEY = "Status-code"
REASON_PHRASE_KEY = "Reason-phrase"

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # remote_ip = get_remote_ip(host)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        result = {}
        request_split_result = data.split("\r\n\r\n")

        header = request_split_result[0]
        header_lines = header.split("\r\n")
        status_line = header_lines[0].split()
        
        result[HTTP_VERSION_KEY] = status_line[0]
        result[STATUS_CODE_KEY] = status_line[1]
        result[REASON_PHRASE_KEY] = status_line[2]
        return int(result[STATUS_CODE_KEY])

    def get_headers(self,data):
        request_split_result = data.split("\r\n\r\n")
            
        header = request_split_result[0]
        header = header.split("\r\n", 1)[1]
        return header

    def get_body(self, data):
        request_split_result = data.split("\r\n\r\n")
        body = request_split_result[1]
        
        return body

    def create_post_body(self, args):
        body = ""
        for key, value in args.items():
            body += key + "=" + value + "&"
        body = body[:-1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):

        o = urllib.parse.urlparse(url)
        host = o.hostname
        port = o.port
        path = o.path
        if path == "":
            path = "/"
        if port == None:
            port = 80

        self.connect(host, port)
        request = f'GET {path} HTTP/1.1\r\n'
        request += f'Host: {host}\r\n'
        request += f'Connection: close\r\n\r\n'
        
        self.sendall(request)

        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        self.get_headers(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        o = urllib.parse.urlparse(url)
        host = o.hostname
        port = o.port
        path = o.path
        if path == "":
            path = "/"
        if port == None:
            port = 80

        self.connect(host, port)
        request = f'POST {path} HTTP/1.1\r\n'
        request += f'Host: {host}\r\n'
        request += f'Connection: close\r\n'
        if args != None:
            message_body = self.create_post_body(args)
            message_body_length = len(message_body.encode('utf-8'))
            request += f'Content-Length: {message_body_length}\r\n\r\n'
            request += message_body
        else:
            request += f'Content-Length: 0\r\n\r\n'
            request += "\r\n"

        self.sendall(request)

        response = self.recvall(self.socket)

        self.close()

        code = self.get_code(response)
        self.get_headers(response)
        body = self.get_body(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
