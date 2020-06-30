from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from threading import Thread
from warnings import warn
INPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
OUTPUT_FILEPATH_PREFIX = './simulation_files/input_vertex_'
FILEPATH_SUFFIX = '.txt'


def vertex(ID):
    filepath = INPUT_FILEPATH_PREFIX + str(ID) + FILEPATH_SUFFIX
    v = Vertex(filepath, ID)
    v.listen_to_master()
    if v.current_round == 1:


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

            self.current_round = 0
            self.color = self.ID

    def send_message(self, message, ip, port):
        # TODO maybe use socket?
        sock_tcp = socket(AF_INET, SOCK_STREAM)
        sock_tcp.sendto(str(message).encode(), (ip, port))
        sock_tcp.close()

        output_filepath = OUTPUT_FILEPATH_PREFIX + str(self.ID) + FILEPATH_SUFFIX
        with open(output_filepath, 'a') as f:
            f.write(message + '_' + str(port))

    def listen_to_master(self):
        # TODO maybe put lock here
        sock_udp = socket(AF_INET, SOCK_DGRAM)
        sock_udp.bind((self.master_IP, self.master_UDP))
        # sock_udp.listen()  # TODO maybe we need this?

        data, addr = sock_udp.recvfrom(4096)
        sock_udp.close()

        return repr(data)

    def send_color_to_children(self):
        threads = []
        for neighbour_ip, neighbour_tcp in zip(self.out_neighbours_IP, self.out_neighbours_TCP):
            threads.append(Thread(target=self.send_message, args=(self.color, neighbour_ip, neighbour_tcp)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()



# v0001 = Vertex('./files/input_vertex_0001.txt')
# pass
