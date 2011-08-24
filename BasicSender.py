import sys
import socket
import random

import Checksum

'''
This is the basic sender class. Your sender will extend this class and will
implement the start() method.
'''
class BasicSender():
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))
        if filename == None:
            self.infile = sys.stdin
        else:
            self.infile = open(filename,"r")
        
    # Waits until packet is received to return.
    def receive(self):
        return self.sock.recv(4096)

    # Sends a packet to the destination address.
    def send(self, message, address=None):
        if address is None:
            address = (self.dest,self.dport)
        self.sock.sendto(message, address)

    # Prepares a packet
    def make_packet(self,msg_type,seqno,msg):
        body = "%s|%d|%s|" % (msg_type,seqno,msg)
        checksum = Checksum.generate_checksum(body)
        packet = "%s%s" % (body,checksum)
        return packet

    # Main sending loop. 
    def start(self):
        raise NotImplementedError
