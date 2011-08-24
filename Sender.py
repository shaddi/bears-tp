import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    # Main sending loop. 
    def start(self):
        raise NotImplementedError

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 
                               "f:p:d:", ["file=", "port=", "dest="])

    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-d ADDRESS | --dest=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-d", "--dest="):
            dest = a
        else:
            print usage()
            exit()

    s = Sender(dest,port,filename)
    s.start()
