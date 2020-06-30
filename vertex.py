from socket import socket, error, AF_INET, SOCK_DGRAM, SOCK_STREAM, SHUT_RDWR, SHUT_WR
from threading import Thread, Lock
import math

INPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
OUTPUT_FILEPATH_PREFIX = './simulation_files/output_vertex_'
COLOR_FILEPATH_PREFIX = './simulation_files/color_vertex_'
FILEPATH_SUFFIX = '.txt'
MAX_UDP_MSG = 4096
LOCALHOST_IP = '127.0.0.1'


def vertex(ID):
    filepath = INPUT_FILEPATH_PREFIX + str(ID) + FILEPATH_SUFFIX
    next_msg = 'next_' + str(ID)
    done_msg = 'done_' + str(ID)
    v = Vertex(filepath, ID)
    while len(v.color) > 3:
        v.socket_to_master.recvfrom(MAX_UDP_MSG)
        v.send_and_receive_colors()
        v.update_color()
        if not v.check_correctness():
            print(f"Runtime Error in 8 coloring."
                  f"ID: {v.ID}"
                  f"Color: {v.color}"
                  f"Parent Color: {v.parent_color}"
                  f"Round: {curr_round}\n")
        v.socket_to_master.sendto(next_msg.encode(), (LOCALHOST_IP, v.master_UDP))

    for i in range(7, 2, -1):
        color_to_reduce = bin(i)[2:].zfill(3)
        v.socket_to_master.recvfrom(MAX_UDP_MSG)
        v.send_and_receive_colors()
        old_color = v.color
        if v.in_neighbour_IP is not None:
            v.color = v.parent_color
            v.send_and_receive_colors()
            neighbouring_colors = {old_color, v.parent_color}
            if v.color == color_to_reduce:
                v.color = minimal_non_conflicting(neighbouring_colors)
        else:
            v.color = minimal_non_conflicting({old_color, old_color})
            v.send_and_receive_colors()
        v.socket_to_master.sendto(next_msg.encode(), (LOCALHOST_IP, v.master_UDP))
    v.socket_to_master.recvfrom(MAX_UDP_MSG)
    color_filepath = COLOR_FILEPATH_PREFIX + str(v.ID) + FILEPATH_SUFFIX
    with open(color_filepath, 'w') as f:
        f.write(v.color[1:])
    assert v.check_correctness()  # TODO Delete
    v.sock_tcp.close()
    v.socket_to_master.sendto(done_msg.encode(), (LOCALHOST_IP, v.master_UDP))

def minimal_non_conflicting(colors):
    if '000' not in colors:
        return '000'
    elif '001' not in colors:
        return '001'
    else:
        return '010'


class Vertex:
    def __init__(self, filepath, ID):
        with open(filepath, 'r') as f:
            self.ID = ID
            self.n_graph_nodes = int(f.readline()[:-1])
            self.master_UDP = int(f.readline()[:-1])
            self.master_IP = f.readline()[:-1]  # IP is string
            self.my_UDP = int(f.readline()[:-1])
            self.my_TCP = int(f.readline()[:-1])

            in_neighbour_tcp = f.readline()[:-1]
            self.in_neighbour_TCP = int(in_neighbour_tcp) if in_neighbour_tcp != 'None' else None

            in_neighbour_ip = f.readline()[:-1]
            self.in_neighbour_IP = in_neighbour_ip if in_neighbour_ip != 'None' else None  # IP is string

            self.out_neighbours_TCP = []
            self.out_neighbours_IP = []
            line = f.readline()[:-1]
            while line != '*':
                self.out_neighbours_TCP.append(int(line))
                self.out_neighbours_IP.append(f.readline()[:-1])
                line = f.readline()[:-1]

            self.color_len = len(self.ID)
            if self.in_neighbour_IP:
                self.color = self.ID
            else:
                self.color = '0' * self.color_len
            self.parent_color = None

            self.socket_to_master = socket(AF_INET, SOCK_DGRAM)
            self.socket_to_master.bind((LOCALHOST_IP, self.my_UDP))
            self.sock_tcp = self.create_socket()

    def send_message_TCP(self, message, ip, port):
        with socket(AF_INET, SOCK_STREAM) as sock_tcp:
            sock_tcp.connect((ip, port))
            sock_tcp.sendall(str(message).encode())

        output_filepath = OUTPUT_FILEPATH_PREFIX + str(self.ID) + FILEPATH_SUFFIX
        with open(output_filepath, 'w') as f:
            f.write(message + '_' + str(port) + "\n")

    def create_socket(self):
        sock_tcp = socket(AF_INET, SOCK_STREAM)
        sock_tcp.bind((LOCALHOST_IP, self.my_TCP))
        sock_tcp.listen()
        return sock_tcp

    def send_and_receive_colors(self):
        self.send_color_to_children()
        if self.in_neighbour_IP is not None:
            conn, _ = self.sock_tcp.accept()
            parent_color = conn.recv(MAX_UDP_MSG)
            self.parent_color = parent_color.decode()

    def send_color_to_children(self):
        for neighbour_ip, neighbour_tcp in zip(self.out_neighbours_IP, self.out_neighbours_TCP):
            self.send_message_TCP(self.color, neighbour_ip, neighbour_tcp)

    def update_color(self):
        """
        :param cp: Parent color
        :return:
        """
        self.color_len = math.ceil(math.log2(self.color_len)) + 1  # TODO potential bug
        if self.in_neighbour_IP is None:
            self.color = '0' * self.color_len
            return self.color
        cp = str(self.parent_color)
        cv = str(self.color)
        for i, (iv, ip) in enumerate(zip(cv, cp)):
            if iv != ip:
                self.color = (bin(i)[2:] + iv).zfill(self.color_len)
                return self.color
        return -1

    def check_correctness(self):
        self.send_and_receive_colors()
        return self.color != self.parent_color
