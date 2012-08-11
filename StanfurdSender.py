import sys
import socket
import random
import getopt

import Checksum
import BasicSender

'''
This StanfurdSender sometimes loses count of sequence numbers.
'''
class StanfurdSender(BasicSender.BasicSender):
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))

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
            rand_added = 0

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif msg == "done":
                msg_type = 'end'
            else:
                rand_added = random.randint(0,1)

            packet = self.make_packet(msg_type, seqno+rand_added, msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive()
            self.handle_response(response)

            if rand_added == 0:
                seqno += 1

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Stanfurd Interactive Sender"
        print "This sender example is bad at counting sequence numbers."
        print "Type 'done' to end the session."
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this help message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "p:a:", ["port=", "address="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a

    s = StanfurdSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
