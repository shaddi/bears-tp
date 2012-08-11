import sys
import socket
import getopt

import Checksum
import BasicSender

'''
This is an unreliable sender class that reads from a file or STDIN.
'''
class UnreliableSender(BasicSender.BasicSender):
    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # Main sending loop.
    def start(self):
        seqno = 0
        msg = self.infile.read(500)
        msg_type = None
        while not msg_type == 'end':
            next_msg = self.infile.read(500)

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'

            packet = self.make_packet(msg_type,seqno,msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive()
            self.handle_response(response)

            msg = next_msg
            seqno += 1

        self.infile.close()

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Unreliable Sender"
        print "Sends data unreliably from a file or STDIN."
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:", ["file=", "port=", "address="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a

    s = UnreliableSender(dest,port,filename)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
