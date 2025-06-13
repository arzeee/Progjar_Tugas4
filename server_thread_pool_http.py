from socket import *
import socket
import os
import time
import sys
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

class HttpServer:
    def proses(self, data):
        lines = data.strip().split("\r\n")
        request_line = lines[0]
        method, path, _ = request_line.split(" ")

        parsed_path = urlparse(path)
        command = parsed_path.path
        query = parse_qs(parsed_path.query)

        logging.info(f"Received request: {method} {path}")

        if method == "GET" and command == "/list":
            return self.list_files()
        elif method == "POST" and command == "/upload":
            return self.upload_file(lines)
        elif method == "DELETE" and command == "/delete":
            filename = query.get('filename', [None])[0]
            return self.delete_file(filename)
        else:
            return self.http_response(404, "Not Found\n")

    def list_files(self):
        try:
            files = os.listdir('.')
            file_list = '\n'.join(files)
            return self.http_response(200, file_list)
        except Exception as e:
            return self.http_response(500, str(e))

    def upload_file(self, lines):
        try:
            headers_ended = False
            body_lines = []
            filename = None

            for line in lines:
                if line.lower().startswith("x-filename:"):
                    filename = line.split(":", 1)[1].strip()
                elif line == '':
                    headers_ended = True
                elif headers_ended:
                    body_lines.append(line)

            if not filename:
                return self.http_response(400, "Filename not provided in header (X-Filename)\n")

            body = '\n'.join(body_lines)
            with open(filename, "w") as f:
                f.write(body)

            logging.info(f"Uploaded file: {filename}")
            return self.http_response(200, f"File '{filename}' uploaded successfully.\n")
        except Exception as e:
            return self.http_response(500, f"Upload error: {str(e)}\n")

    def delete_file(self, filename):
        if not filename:
            return self.http_response(400, "Filename not provided\n")

        try:
            os.remove(filename)
            logging.info(f"Deleted file: {filename}")
            return self.http_response(200, f"File '{filename}' deleted successfully.\n")
        except FileNotFoundError:
            return self.http_response(404, "File not found\n")
        except Exception as e:
            return self.http_response(500, f"Delete error: {str(e)}\n")

    def http_response(self, status_code, content):
        reason = {
            200: "OK",
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error"
        }.get(status_code, "OK")
        response = f"HTTP/1.1 {status_code} {reason}\r\nContent-Length: {len(content)}\r\n\r\n{content}\r\n\r\n"
        return response.encode()


httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv = ""
    try:
        while True:
            data = connection.recv(1024)
            if data:
                d = data.decode()
                rcv += d
                if rcv.endswith('\r\n\r\n') or '\r\n\r\n' in rcv:
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + b"\r\n\r\n"
                    connection.sendall(hasil)
                    logging.info(f"Finished processing request from {address}")
                    break
            else:
                break
    except Exception as e:
        logging.error(f"Error with client {address}: {e}")
    finally:
        connection.close()


def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(5)

    logging.info("Server running on port 8889 using ThreadPool")

    with ThreadPoolExecutor(max_workers=20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            logging.info(f"Accepted connection from {client_address}")
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)

            aktif = sum(1 for t in the_clients if not t.done())
            logging.info(f"Jumlah thread aktif: {aktif}")


# Entry point
if __name__ == "__main__":
    Server()
