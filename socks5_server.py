import socketserver
import socks
import threading
import socket

# Простейший SOCKS5 сервер на базе PySocks
# Для production стоит использовать более защищённые реализации!
from socketserver import ThreadingMixIn, TCPServer

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True

class Socks5Handler(socketserver.BaseRequestHandler):
    def handle(self):
        # Используем PySocks как библиотеку для обработки SOCKS
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, "localhost", 1080)
        try:
            while True:
                data = self.request.recv(4096)
                if not data:
                    break
                s.sendall(data)
                resp = s.recv(4096)
                self.request.sendall(resp)
        except Exception as e:
            pass
        finally:
            s.close()
            self.request.close()

def start_server(host="0.0.0.0", port=1080):
    server = ThreadedTCPServer((host, port), Socks5Handler)
    print(f"SOCKS5 Server started at {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    input("SOCKS5 сервер запущен. Нажмите Enter для выхода...\n")
