#Based on server_threads.py
#https://gist.github.com/gordinmitya/349f4abdc6b16dc163fa39b55544fd34

import socket
from threading import Thread
import os

BLOCK_SIZE = 1024

class ClientListener(Thread):
	def __init__(self, name: str, sock: socket.socket):
		super().__init__(daemon=True)
		self.sock = sock
		self.name = name


	def _close(self):
		self.sock.close()
		print(self.name + ' disconnected')



	def run(self):
		#recieve information about file
		file_info = (self.sock.recv(BLOCK_SIZE)).decode()
		file_size = int(file_info.split()[0])
		file_name = file_info.split()[1]
		file_name, file_format = file_name.split('.')
		#caculate number of 1KB chunks in the file
		#and size of remaining data
		n_blocks = file_size//BLOCK_SIZE
		extra_block = file_size - n_blocks*BLOCK_SIZE

		#check name colisions
		copy=0
		if os.path.isfile(file_name+'.'+file_format):
			copy = 1
			while os.path.isfile('{}({}).{}'.format(file_name, copy, file_format)):
				copy += 1
		
		#if some copies already exist change name
		# to name(n).formats
		#otherwise use name.format
		file = '{}.{}'.format(file_name, file_format)
		if copy != 0:
			file = '{}({}).{}'.format(file_name, copy, file_format)
			print('name colision, using ' + file)


		#create file in append binary mode
		f = open(file, 'ab')

		#recieve data and write to file
		for i in range(n_blocks):
			block = self.sock.recv(BLOCK_SIZE)
			f.write(block)

		block = self.sock.recv(extra_block)
		f.write(block)

		f.close()
		print('{} bytes recieved, closing conection'.format(file_size))
		#close connection
		self._close()
			



				

def main():
	next_name = 1

	# AF_INET – IPv4, SOCK_STREAM – TCP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# reuse address; in OS address will be reserved after app closed for a while
	# so if we close and imidiatly start server again – we'll get error
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# listen to all interfaces at 6342 port
	sock.bind(('', 6342))
	sock.listen()
	while True:
		# blocking call, waiting for new client to connect
		con, addr = sock.accept()
		name = 'u' + str(next_name)
		next_name += 1
		print(str(addr) + ' connected as ' + name)
		ClientListener(name, con).start()


if __name__ == "__main__":
	main()