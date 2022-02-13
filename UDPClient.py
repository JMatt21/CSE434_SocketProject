from socket import *
import atexit # for exit_handler() and atexit.register

serverName = '129.219.10.241'
serverPort = 6250
clientSocket = socket(AF_INET, SOCK_DGRAM)

clientName = ""
hasDeregistered = False

# de-registers the user upon exit, whether through
# the exit command or by keyboard interrupt 
def exit_handler():
	print("bye bye")
	clientSocket.sendto("exit".encode(),(serverName, serverPort))
	clientSocket.close()

atexit.register(exit_handler)

while (True):
		message = raw_input('Type a command here: ') # raw_input is used because general2 is running python 2.7.5
		command = tuple(map(str, message.split(' ')))
		clientSocket.sendto(message.encode(),(serverName, serverPort))

		returned_message, serverAddress = clientSocket.recvfrom(2048)

		if (command[0] == "exit"):
			exit()
		else:
			print(returned_message.decode())