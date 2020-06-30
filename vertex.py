import math
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread
from warnings import warn
INPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
OUTPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
FILEPATH_SUFFIX = '.txt'
BUFF_SIZE = 4096

# TODO why no root?


def vertex(ID):
    filepath = INPUT_FILEPATH_PREFIX + str(ID) + FILEPATH_SUFFIX
    v = Vertex(filepath, ID)


class Vertex:
    def __init__(self, filepath, ID):
        with open(filepath, 'r') as f:
            self.ID = ID  # TODO add ID
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

            self.color = self.ID
            self.parent_color = None
            self.color_len = len(self.ID)

    def send_message_TCP(self, message, ip, port):
        assert type(port) == int
        with socket(AF_INET, SOCK_STREAM) as sock_tcp:
            sock_tcp.connect((ip, port))
            sock_tcp.sendall(str(message).encode())

        output_filepath = OUTPUT_FILEPATH_PREFIX + str(self.ID) + FILEPATH_SUFFIX
        with open(output_filepath, 'a') as f:
            f.write(message + '_' + str(port))

    def listen_to_master(self):
        # TODO maybe put lock here
        with socket(AF_INET, SOCK_DGRAM) as sock_udp:
            sock_udp.bind(('127.0.0.1', self.my_UDP))  # TODO why use hard coded IP
            data, _ = sock_udp.recvfrom(BUFF_SIZE)
            return data.decode()

    def listen_to_parent(self):
        with socket(AF_INET, SOCK_STREAM) as sock_tcp:
            sock_tcp.bind((self.in_neighbour_IP, self.in_neighbour_TCP))
            conn, addr = sock_tcp.accept()
            msg = conn.recv(BUFF_SIZE)
            self.parent_color = msg.decode()

    def send_color_to_children(self):
        threads = []
        for neighbour_ip, neighbour_tcp in zip(self.out_neighbours_IP, self.out_neighbours_TCP):
            threads.append(Thread(target=self.send_message_TCP, args=(self.color, neighbour_ip, neighbour_tcp)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def update_color(self):
        """

        :param cp: Parent color
        :return:
        """
        self.color_len = math.ceil(math.log2(self.color_len)) + 1  # TODO potential bug
        cp = str(self.parent_color)
        cv = str(self.color)
        for i, iv, ip in enumerate(zip(cv, cp)):
            if iv != ip:
                self.color = (bin(i)[2:] + iv).zfill(self.color_len)
                return self.color
        return -1

    def finish_round(self):
        """
        Notifies master that self has finished thee current round
        """
        # self.send_message_TCP('next_' + str(self.ID), self.master_IP, self.master_UDP)
        # TODO die

    def init_parent_socket(self):
        parent_socket = socket(AF_INET, SOCK_STREAM)
        parent_socket.bind((self.in_neighbour_IP, self.in_neighbour_TCP))
        conn, _ = parent_socket.accept()
        self.parent_conn = conn

    def init_children_sockets(self):
        for child_ip, child_tcp in zip(self.out_neighbours_IP, self.out_neighbours_TCP):
            sock_tcp = socket(AF_INET, SOCK_STREAM)
            sock_tcp.connect((child_ip, child_tcp))
            self.children_sockets.append(sock_tcp)
