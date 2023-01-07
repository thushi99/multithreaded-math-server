import socket
from subprocess import Popen, STDOUT, PIPE
from threading import Thread

def start_new_math_thread(conn, addr):
    t = MathServerCommunicationThread(conn, addr)
    t.start()

class ProcessOutputThread(Thread):
    def __init__(self, proc, conn):
        Thread.__init__(self)
        self.proc = proc
        self.conn = conn

    def run(self):
        while not self.proc.stdout.closed and not self.conn._closed:
            try:
                self.conn.sendall(self.proc.stdout.readline())
            except:
                pass

class MathServerCommunicationThread(Thread):
    def __init__(self, conn, adr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print("{} Connected with back port {}".format(self.addr[0], self.addr[1]))
        self.conn.sendall("    __  ___        __   __       _____                               \n   /  |/  /____ _ / /_ / /_     / ___/ ___   _____ _   __ ___   _____\n  / /|_/ // __ `// __// __ \    \__ \ / _ \ / ___/| | / // _ \ / ___/\n / /  / // /_/ // /_ / / / /   ___/ //  __// /    | |/ //  __// /    \n/_/  /_/ \__,_/ \__//_/ /_/   /____/ \___//_/     |___/ \___//_/     \n\tMulti Threaded Math Server developed by Thushitharan\n\n\tGive any Math expressions, and I will answer you :)\n\n$".encode())

        p = Popen(['bc'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = ProcessOutputThread(p, self.conn)
        output.start()

        while not p.stdout.closed or not self.conn._closed:
            try:
                data = self.conn.recv(1024)
                if not data:
                    break
                else:
                    try:
                        data = data.decode()
                        query = data.strip()
                        if query == 'quit' or query == 'exit':
                            p.communicate(query.encode(), timeout=1)
                            if p.poll() is not None:
                                break
                        query = query + '\n'
                        p.stdin.write(query.encode())
                        p.stdin.flush()
                    except:
                        pass
            except:
                pass
        self.conn.close()

HOST = ''
PORT = 8877

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()

while True:
    conn, addr = s.accept()
    start_new_math_thread(conn, addr)
s.close()
