from socket import *

def register(user, IPv4, port):
	# print(user)
	# print(IPv4)
	# print(port)
	new_user = (user, IPv4, port, False)

	for r_user in registered_users:
		if (r_user[0] == user):
			return "FAILURE - Username already exists."
		elif (r_user[1] == IPv4 and r_user[2] == port):
			de_register(r_user[0])
			registered_users.append(new_user)
			return "SUCCESS"

	# create and append the new user
	registered_users.append(new_user)
	# print(registered_users)
	return "SUCCESS"

def de_register(user):
	for r_user in registered_users:
		if (r_user[0] == user and r_user[3] == False):
			registered_users.remove(r_user)
			return "SUCCESS"

	return "FAILURE"

def query_players():
	ret = ""
	for r_user in registered_users:
		ret += (r_user[0] + ": " + r_user[1] + ":" + str(r_user[2]) + "\n")
	return ret

def query_games():
	return str(concurrent_games.__sizeof__) + "total games."

def game_start(user, k):
	print()

def game_end(game_id, user_dealer):
	print()

serverPort = 6250
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
registered_users = []
concurrent_games = []


print("The server is ready to receive")
while True:
	message, clientAddress = serverSocket.recvfrom(2048)
	modifiedMessage = message.decode().upper()
	#serverSocket.sendto(modifiedMessage.encode(), clientAddress)

	command = tuple(map(str, message.decode().split(' ')))

	if   (command[0] == "register"):
		serverSocket.sendto( register(command[1], clientAddress[0], clientAddress[1]).encode(), clientAddress )
	elif (command[0] == "dereg"):
		serverSocket.sendto( de_register(command[1]).encode(), clientAddress )
	elif (command[0] == "qp"):
		serverSocket.sendto( query_players().encode(), clientAddress)
	elif (command[0] == "qg"):
		serverSocket.sendto( query_games().encode(), clientAddress)
	else:
		serverSocket.sendto(modifiedMessage.encode(), clientAddress)