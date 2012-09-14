import socket
import getopt
import sys
import time

import Checksum

class Connection():
    def __init__(self,host,port,start_seq,debug=False):
        self.debug = debug
        self.updated = time.time()
        self.current_seqno = start_seq - 1 # expect to ack from the start_seqno
        self.host = host
        self.port = port
        self.max_buf_size = 5
        self.outfile = open("%s.%d" % (host,port),"w")
        self.seqnums = {} # enforce single instance of each seqno

    def ack(self,seqno, data):
        res_data = []
        self.updated = time.time()
        if seqno > self.current_seqno and seqno <= self.current_seqno + self.max_buf_size:
            self.seqnums[seqno] = data
            for n in sorted(self.seqnums.keys()):
                if n == self.current_seqno + 1:
                    self.current_seqno += 1
                    res_data.append(self.seqnums[n])
                    del self.seqnums[n]
                else:
                    break # when we find out of order seqno, quit and move on

        if self.debug:
            print "next seqno should be %d" % (self.current_seqno+1)

        # note: we return the /next/ sequence number we're expecting
        return self.current_seqno+1, res_data

    def record(self,data):
        self.outfile.write(data)
        self.outfile.flush()

    def end(self):
        self.outfile.close()

class Receiver():
    def __init__(self,listenport=33122,debug=False,timeout=10):
        self.debug = debug
        self.timeout = timeout
        self.last_cleanup = time.time()
        self.port = listenport
        self.host = ''
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(timeout)
        self.s.bind((self.host,self.port))
        self.connections = {} # schema is {(address, port) : Connection}
        self.MESSAGE_HANDLER = {
            'start' : self._handle_start,
            'data' : self._handle_data,
            'end' : self._handle_end,
            'ack' : self._handle_ack
        }

    def start(self):
        while True:
            try:
                message, address = self.receive()
                msg_type, seqno, data, checksum = self._split_message(message)
                try:
                    seqno = int(seqno)
                except:
                    raise ValueError
                if debug:
                    print "%s %d %s %s" % (msg_type, seqno, data, checksum)
                if Checksum.validate_checksum(message):
                    self.MESSAGE_HANDLER.get(msg_type,self._handle_other)(seqno, data, address)
                elif self.debug:
                    print "checksum failed: %s" % message

                if time.time() - self.last_cleanup > self.timeout:
                    self._cleanup()
            except socket.timeout:
                self._cleanup()
            except (KeyboardInterrupt, SystemExit):
                exit()
            except ValueError, e:
                if self.debug:
                    print e
                pass # ignore

    # waits until packet is received to return
    def receive(self):
        return self.s.recvfrom(4096)

    # sends a message to the specified address. Addresses are in the format:
    #   (IP address, port number)
    def send(self, message, address):
        self.s.sendto(message, address)

    # this sends an ack message to address with specified seqno
    def _send_ack(self, seqno, address):
        m = "ack|%d|" % seqno
        checksum = Checksum.generate_checksum(m)
        message = "%s%s" % (m, checksum)
        self.send(message, address)

    def _handle_start(self, seqno, data, address):
        if not address in self.connections:
            self.connections[address] = Connection(address[0],address[1],seqno,self.debug)
        conn = self.connections[address]
        ackno, res_data = conn.ack(seqno,data)
        for l in res_data:
            if self.debug:
                print data
            conn.record(l)
        self._send_ack(ackno, address)

    # ignore packets from uninitiated connections
    def _handle_data(self, seqno, data, address):
        if address in self.connections:
            conn = self.connections[address]
            ackno,res_data = conn.ack(seqno,data)
            for l in res_data:
                if self.debug:
                    print l
                conn.record(l)
            self._send_ack(ackno, address)

    # handle end packets
    def _handle_end(self, seqno, data, address):
        if address in self.connections:
            conn = self.connections[address]
            ackno, res_data = conn.ack(seqno,data)
            for l in res_data:
                if self.debug:
                    print l
                conn.record(l)
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

    def _cleanup(self):
        if self.debug:
            print "clean up time"
        now = time.time()
        for address in self.connections.keys():
            conn = self.connections[address]
            if now - conn.updated > self.timeout:
                if self.debug:
                    print "killed connection to %s (%.2f old)" % (address, now - conn.updated)
                conn.end()
                del self.connections[address]
        self.last_cleanup = now

if __name__ == "__main__":
    def usage():
        print "BEARS-TP Receiver"
        print "-p PORT | --port=PORT The listen port, defaults to 33122"
        print "-t TIMEOUT | --timeout=TIMEOUT Receiver timeout in seconds"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "p:dt:", ["port=", "debug=", "timeout="])
    except:
        usage()
        exit()

    port = 33122
    debug = False
    timeout = 10

    for o,a in opts:
        if o in ("-p", "--port="):
            port = int(a)
        elif o in ("-t", "--timeout="):
            timeout = int(a)
        elif o in ("-d", "--debug="):
            debug = True
        else:
            print usage()
            exit()
    r = Receiver(port, debug, timeout)
    r.start()
