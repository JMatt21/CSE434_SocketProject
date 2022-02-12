from socket import *

def register(user, IPv4, port):
	print("test")

def de_register(user):
	print("test")

def query_players():
	print("test")

def query_games():
	print("test")

def game_start(user, k):
	print()

def game_end(game_id, user_dealer):
	print()

serverPort = 6250
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("The server is ready to receive")
while True:
 message, clientAddress = serverSocket.recvfrom(2048)
 print(type(clientAddress))
 modifiedMessage = message.decode().upper()
 serverSocket.sendto(modifiedMessage.encode(), clientAddress)