import sys
import socket
import random
import getopt

import Checksum

'''
This is a simple interactive sender.
'''
class InteractiveSender():
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))
        
    # Waits until packet is received to return.
    def receive(self):
        return self.sock.recv(4096)

    # Sends a packet to the destination address.
    def send(self, message):
        self.sock.sendto(message, (self.dest,self.dport))

    # Prepares a packet
    def make_packet(self,msg_type,seqno,msg):
        body = "%s|%d|%s|" % (msg_type,seqno,msg)
        checksum = Checksum.generate_checksum(body)
        packet = "%s%s" % (body,checksum)
        return packet

    # Handles a response from the receiver. 
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # Main sending loop. 
    def start(self):
        seqno = 0
        msg_type = None
        while not msg_type == 'end':
            msg = raw_input("Message:")

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif msg == "done":
                msg_type = 'end'

            packet = self.make_packet(msg_type, seqno, msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive()
            self.handle_response(response)

            seqno += 1

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Interactive Sender"
        print "Type 'done' to end the session."
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-d ADDRESS | --dest=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                               "p:d:", ["port=", "dest="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-p", "--port="):
            port = int(a)
        elif o in ("-d", "--dest="):
            dest = a

    s = InteractiveSender(dest,port,filename)
    s.start()
