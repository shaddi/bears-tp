import socket

import Checksum

class Connection():
    def __init__(self,host,port,start_seq):
        self.current_seqno = start_seq
        self.host = host
        self.port = port
        self.outfile = open("%s.%d" % (host,port),"w")
        self.seqnums = {} # enforce single instance of each seqno

    def ack(self,seqno, data):
        res_data = []
        if seqno < self.current_seqno + 50: # don't be greedy with my buffer
            self.seqnums[seqno] = data 
            for n in sorted(self.seqnums.keys()):
                if n == self.current_seqno + 1:
                    self.current_seqno += 1
                    res_data.append(self.seqnums[n])
                    del self.seqnums[n]
                else:
                    break # when we find out of order seqno, quit and move on
        return self.current_seqno, res_data

    def record(self,data):
        self.outfile.write(data)

    def end(self):
        self.outfile.close()

class Server():
    def __init__(self,listenport=33122):
        self.port = 33122
        self.host = ''
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host,self.port))
        self.connections = {} # {(address, port) : Connection}
        self.MESSAGE_HANDLER = {
            'syn' : self._handle_syn,
            'data' : self._handle_data,
            'end' : self._handle_end,
            'ack' : self._handle_ack
        }
        
    def start(self):
        while True:
            try:
                message, address = self.s.recvfrom(8192)
                msg_type, seqno, data, checksum = self._split_message(message)
                try:
                    seqno = int(seqno)
                except:
                    raise ValueError
                print "%s %d %s %s" % (msg_type, seqno, data, checksum)
                if Checksum.validate_checksum(message):
                    self.MESSAGE_HANDLER.get(msg_type,self._handle_other)(seqno, data, address)
            except (KeyboardInterrupt, SystemExit):
                raise
            #except (ValueError):
            #    pass # ignore

    # this sends an ack message to address with specified seqno
    def _send_ack(self, seqno, address):
        m = "ack|%d|" % seqno
        checksum = Checksum.generate_checksum(m)
        message = "%s%s" % (m, checksum)
        self.s.sendto(message, address)

    def _handle_syn(self, seqno, data, address):
        conn = Connection(address[0],address[1],seqno)
        self.connections[address] = conn
        print data
        conn.record(data)
        self._send_ack(seqno, address)

    # ignore packets from uninitiated connections
    def _handle_data(self, seqno, data, address): 
        if address in self.connections:
            conn = self.connections[address]
            ackno,res_data = conn.ack(seqno,data)
            for l in res_data:
                print l
                conn.record(l)
            self._send_ack(ackno, address)

    # if we're not missing packets, end the connection. Otherwise keep it
    # alive.
    def _handle_end(self, seqno, data, address):
        if address in self.connections:
            conn = self.connections[address]
            ackno, res_data = conn.ack(seqno,data)
            for l in res_data:
                print l
                conn.record(l)
            if ackno == seqno: # we're done, kill this connection
                conn.end()
                del self.connections[address]
            self._send_ack(ackno, address)

    # I'll do the ack-ing here, buddy
    def _handle_ack(self, seqno, data, address):
        pass

    # handler for packets with unrecognized type
    def _handle_other(self, seqno, data, address):
        pass


    def _split_message(self, message):
        pieces = message.split('|')
        msg_type, seqno = pieces[0:2] # first two elements always treated as msg type and seqno
        checksum = pieces[-1] # last is always treated as checksum
        data = '|'.join(pieces[2:-1]) # everything in between is considered data
        return msg_type, seqno, data, checksum

if __name__ == "__main__":
    s = Server()
    s.start()
