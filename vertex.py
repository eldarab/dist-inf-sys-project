import math
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread
from warnings import warn
INPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
OUTPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
FILEPATH_SUFFIX = '.txt'
BUFF_SIZE = 4096


def vertex(ID):
    filepath = INPUT_FILEPATH_PREFIX + str(ID) + FILEPATH_SUFFIX
    v = Vertex(filepath, ID)
    while v.color_len > 3:
        master_msg = v.listen_to_master()  # master sends current round
        if master_msg == 'DIE':
            break
        parent_listener = Thread(target=v.listen_to_parent)
        parent_listener.start()
        v.send_color_to_children()
        parent_listener.join()
        v_color = v.update_color()
        assert v_color != -1
        v.finish_round()


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
                self.out_neighbours_TCP.append(line)
                self.out_neighbours_IP.append(f.readline()[:-1])
                line = f.readline()[:-1]

            self.color = self.ID
            self.parent_color = None
            self.color_len = len(self.ID)

    def send_message_TCP(self, message, ip, port):
        sock_tcp = socket(AF_INET, SOCK_STREAM)
        sock_tcp.bind((ip, int(port)))
        sock_tcp.sendto(str(message).encode(), (ip, int(port)))
        sock_tcp.close()

        output_filepath = OUTPUT_FILEPATH_PREFIX + str(self.ID) + FILEPATH_SUFFIX
        with open(output_filepath, 'a') as f:
            f.write(message + '_' + str(port))

    def listen_to_master(self):
        # TODO maybe put lock here
        sock_udp = socket(AF_INET, SOCK_DGRAM)
        sock_udp.bind(('127.0.0.1', self.my_UDP))  # TODO why use hard coded IP
        # sock_udp.listen()  # TODO maybe we need this?
        data, addr = sock_udp.recvfrom(BUFF_SIZE)
        sock_udp.close()
        return repr(data)

    def listen_to_parent(self):
        sock_tcp = socket(AF_INET, SOCK_STREAM)
        sock_tcp.bind((self.in_neighbour_IP, str(self.in_neighbour_TCP)))
        msg = sock_tcp.recvfrom(BUFF_SIZE)
        sock_tcp.close()
        self.parent_color = repr(msg)

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

# v0001 = Vertex('./files/input_vertex_0001.txt')
# pass
