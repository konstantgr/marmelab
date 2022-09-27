import socket
import threading


def emulator(ip="127.0.0.1", port=9000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data[0:3] == b'APS':
                    data += b'10,20,30,40>'
                elif data[0:3] == b'ASP':
                    data += b'10,20,30,40>'
                elif data[0:3] == b'AAC':
                    data += b'10,20,30,40>'
                elif data[0:3] == b'ADC':
                    data += b'10,20,30,40>'
                conn.sendall(data)


def run(blocking=True, ip="127.0.0.1", port=9000):
    server_thread = threading.Thread(target=emulator, args=(ip, port,))
    print('Starting server')
    server_thread.start()
    if blocking:
        server_thread.join()


if __name__ == "__main__":
    run()
