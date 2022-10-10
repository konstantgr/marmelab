import socket
from src import Position, Velocity, Acceleration, Deceleration, BaseAxes
import threading
import time
from dataclasses import dataclass


@dataclass
class ScannerStorage:
    acceleration = Acceleration(10, 20, 30, 40)
    deceleration = Deceleration(10, 20, 30, 40)
    velocity = Velocity(10, 20, 30, 40)
    position = Position(10, 20, 30, 40)
    absolute_position = Position(10, 20, 30, 40)
    motor_on = BaseAxes(0, 0, 0, 0)
    motion_mode = BaseAxes(0, 0, 0, 0)
    special_motion_mode = BaseAxes(0, 0, 0, 0)

    motor_status = BaseAxes(0, 0, 0, 0)
    error_motion = BaseAxes(1, 1, 1, 1)
    motion_start_time = BaseAxes(time.time(), time.time(), time.time(), time.time())


def return_by_cmd(axis: BaseAxes, letter: bytes) -> bytes:
    if letter == b'A':
        return f'{axis.x},{axis.y},{axis.z},{axis.w}>'.encode()
    elif letter == b'X':
        return f'{axis.x}>'.encode()
    elif letter == b'Y':
        return f'{axis.y}>'.encode()
    elif letter == b'Z':
        return f'{axis.z}>'.encode()
    elif letter == b'W':
        return f'{axis.w}>'.encode()


def set_by_cmd(axis: BaseAxes, letter: bytes, cmd: bytes) -> bytes:
    try:
        if letter == b'A':
            axis.x = int(cmd.split(b',')[0])
            axis.y = int(cmd.split(b',')[1])
            axis.z = int(cmd.split(b',')[2])
            axis.w = int(cmd.split(b',')[3])
        elif letter == b'X':
            axis.x = int(cmd)
        elif letter == b'Y':
            axis.y = int(cmd)
        elif letter == b'Z':
            axis.z = int(cmd)
        elif letter == b'W':
            axis.w = int(cmd)
        return b'>'
    except:
        return b'?>'


def update_ms_em(scanner, tmp, motion_time):
    if tmp - scanner.motion_start_time.x < motion_time:
        scanner.motor_status.x = 1
        scanner.error_motion.x = 0
    else:
        scanner.motor_status.x = 0
        scanner.error_motion.x = 1
        scanner.position.x = scanner.absolute_position.x
    if tmp - scanner.motion_start_time.y < motion_time:
        scanner.motor_status.y = 1
        scanner.error_motion.y = 0
    else:
        scanner.motor_status.y = 0
        scanner.error_motion.y = 1
        scanner.position.y = scanner.absolute_position.y
    if tmp - scanner.motion_start_time.z < motion_time:
        scanner.motor_status.z = 1
        scanner.error_motion.z = 0
    else:
        scanner.motor_status.z = 0
        scanner.error_motion.z = 1
        scanner.position.z = scanner.absolute_position.z
    if tmp - scanner.motion_start_time.w < motion_time:
        scanner.motor_status.w = 1
        scanner.error_motion.w = 0
    else:
        scanner.motor_status.w = 0
        scanner.error_motion.w = 1
        scanner.position.w = scanner.absolute_position.w


def emulator(ip="127.0.0.1", port=9000, motion_time: int = 5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        conn, addr = s.accept()
        scanner = ScannerStorage()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                if not data.endswith(b';'):
                    raise RuntimeError
                new_data = data

                axis = None
                done = False
                if data[1:3] == b'PS':
                    axis = scanner.position
                elif data[1:3] == b'AP':
                    axis = scanner.absolute_position
                elif data[1:3] == b'SP':
                    axis = scanner.velocity
                elif data[1:3] == b'AC':
                    axis = scanner.acceleration
                elif data[1:3] == b'DC':
                    axis = scanner.deceleration
                elif data[1:3] == b'MO':
                    axis = scanner.motor_on
                elif data[1:3] == b'MM':
                    axis = scanner.motion_mode
                elif data[1:3] == b'SM':
                    axis = scanner.special_motion_mode

                elif data[1:3] == b'BG':
                    letter = data[0:1]
                    if letter == b'A':
                        tmp = time.time()
                        scanner.motion_start_time = BaseAxes(tmp, tmp, tmp, tmp)
                    elif letter == b'X':
                        scanner.motion_start_time.x = time.time()
                    elif letter == b'Y':
                        scanner.motion_start_time.y = time.time()
                    elif letter == b'Z':
                        scanner.motion_start_time.z = time.time()
                    elif letter == b'W':
                        scanner.motion_start_time.z = time.time()
                    update_ms_em(scanner, time.time(), motion_time)
                    new_data += b'>'
                    done = True

                elif data[1:3] == b'MS':
                    update_ms_em(scanner, time.time(), motion_time)
                    axis = scanner.motor_status
                elif data[1:3] == b'EM':
                    update_ms_em(scanner, time.time(), motion_time)
                    axis = scanner.error_motion

                if axis is None and not done:
                    new_data += b'?>'
                elif not done:
                    if data.count(b'=') == 0:
                        new_data += return_by_cmd(axis, data[0:1])
                    elif data[3:4] == b'=':
                        new_data += set_by_cmd(axis, data[0:1], data[4:-1])
                    else:
                        new_data += b'?>'
                conn.sendall(new_data)


def run(blocking=True, ip="127.0.0.1", port=9000, motion_time=5):
    server_thread = threading.Thread(target=emulator, args=(ip, port, motion_time))
    print('Starting server')
    server_thread.start()
    if blocking:
        server_thread.join()


if __name__ == "__main__":
    run()
