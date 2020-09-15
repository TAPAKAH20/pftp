import argparse
import os
import socket

BLOCK_SIZE = 1024

parser = argparse.ArgumentParser()
parser.add_argument('file', help='path to the file (no spaces in the name)')
parser.add_argument('addres', help='ip or url of the server')
parser.add_argument('port', help='port to use, server is running on 6342', type=int, default=6342)

#parse arguments
args = parser.parse_args()
path = args.file
addres = args.addres
port = args.port


#create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect to server
print('Connecting to {}:{}'.format(addres, port))
sock.connect((addres, port))


#reading info about file
file_name = path.split()[-1]
file_size = os.path.getsize(path)
#open file in binary mode
f = open(path, 'rb')


#pad file_info to be 1 KB
file_info = str(file_size) + ' ' + file_name
file_info += ' '*(BLOCK_SIZE - len(file_info))
#and send it as first packet
sock.send(file_info.encode())

#caculate number of 1KB chunks in the file
#caculate number of 1KB chunks in the file
#and size of remaining data
n_blocks = file_size//BLOCK_SIZE
extra_block = file_size - n_blocks*BLOCK_SIZE


#send blocks
#progress bar was made with the help of one of the answers on
#https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
for i in range(n_blocks):
	data = f.read(BLOCK_SIZE)
	sock.send(data)
	progress = i/n_blocks
	print("\r[{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress*100), end="", flush=True)
print()

#send remaining
data = f.read(extra_block)
sock.send(data)

#close connection
sock.close()

print('Operation sucsesssful')