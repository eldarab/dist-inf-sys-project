def vertex(ID):
    pass


class Vertex:
    def __init__(self, filepath):
        with open(filepath, 'r') as f:
            self.ID = 0  # TODO add ID
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

    def send_message(self, message, port):
        """
        Sends a message to a neighbour and writes it to a file
        :param message: The message content to send
        :param port: The TCP port the neighbour is listening to in order to receive messages
        """
        # TODO maybe use socket?
        if port != self.in_neighbour_TCP and port not in self.out_neighbours_TCP:
            raise Exception('Receiver is not a neighbour')
        output_filepath = './files/output_vertex_' + str(self.ID) + '.txt'
        with open(output_filepath, 'a') as f:
            f.write(message + '_' + str(port))


v0001 = Vertex('./files/input_vertex_0001.txt')
