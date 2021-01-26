#  coding: utf-8
import socketserver
import os
from pathlib import Path
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def getMethod(self):
        return self.data.splitlines()[0].split()[0]

    def getPath(self):
        return self.data.splitlines()[0].split()[1]

    def getFilePath(self, path):
        filePath = os.getcwd() + self.parentFolder + path
        if(path.endswith('/')):
            filePath += 'index.html'
        return filePath

    def pathCheck(self, path):
        return os.path.exists(os.path.abspath(os.getcwd() + self.parentFolder + path))

    def openFile(self, filePath):
        file = open(filePath, 'rb')
        response = file.read()
        file.close()
        return response

    def getMimeType(self, filePath):
        if(filePath.endswith(".css")):
            return 'text/css\r\n'
        return 'text/html\r\n'

    def response405(self):
        return ('HTTP/1.1 405 Method Not Allowed\n\n', '<html><body><center><h3>Error 405: Method Not Allowed</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8'))

    def response404(self):
        return ('HTTP/1.1 404 Not Found\n\n', '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8'))
    
    def response301(self):
        return ('HTTP/1.1 301 Not Found\n\n', '<html><body><center><h3>Error 301: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode(
            'utf-8'))

    def handle(self):
        self.parentFolder = "/www"
        self.data = self.request.recv(1024).strip().decode('utf-8')
        # self.request.sendall(bytearray("OK", 'utf-8'))
        print("Got a request of: %s\n" % self.data)

        # Get method and path
        method = self.getMethod()
        path = self.getPath()
        filePath = self.getFilePath(path)

        # print(os.path.isfile(os.path.abspath(
        #     os.getcwd() + self.parentFolder + filePath)))
        print(os.path.isfile(filePath))

        if method != "GET":
            header, response = self.response405()

        else:
            try:
                if(not (os.path.isfile(filePath)) and self.pathCheck(path)):
                    header, response = self.response301()
                else:
                    header = 'HTTP/1.1 200 OK\r\n'
                    response = self.openFile(filePath)
                    mimetype = self.getMimeType(filePath)
                    header += 'Content-Type: ' + mimetype + '\n\n'

            except Exception as e:
                header, response = self.response404()

        final_response = header.encode('utf-8')
        final_response += response
        self.request.sendall(final_response)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
