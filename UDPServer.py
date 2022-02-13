from socket import *

# this function takes 3 arguements: str user, str IPv4, int port
# It creates a new user to append to registeredUsers by default
# if a Username already exists, then it returns "FAILURE" and the server sends
# a message back to the client
# If a user tries to register another name, it will change their own Username
# however, this puts them at the end of the list, registeredUsers. 
def register(user, IPv4, port):
	# Our X-tuple is used to store the data of each user
	# Current structure of users
	# (Username, IPv4 Address, port #, inAGame, cards)
	#     [0]        [1]        [2]      [3]     [4]
	new_user = (user, IPv4, port, False, [])

	for r_user in registered_users:
		# If a user with the same name already exists
		if (r_user[0] == user):
			return "FAILURE"
		# Used for renaming a user on the same connection
		elif (r_user[1] == IPv4 and r_user[2] == port):
			de_register(r_user[0])
			registered_users.append(new_user)
			return "SUCCESS"

	# create and append the new user
	registered_users.append(new_user)

	return "SUCCESS"

# This function takes one argument, str user
# As long as that user is not in a game, it will de-register them
# returns "SUCCESS" on a removal, and "FAILURE" when it can't find the specific user
def de_register(user):
	for r_user in registered_users:
		if (r_user[0] == user and r_user[3] == False):
			registered_users.remove(r_user)
			print("De-registering: " + r_user[0] + ".")
			return "SUCCESS"

	return "FAILURE"

# This function takes all the users in registeredUsers
# and returns a string in the form of 'username': 111.222.333:00000
def query_players():
	ret = ""
	for r_user in registered_users:
		ret += (r_user[0] + ": " + r_user[1] + ":" + str(r_user[2]) + "\n")
	return ret

# This function returns the number of games currently running at the moment
# will later return a message with the game data
def query_games():
	numOfGames = len(concurrent_games)
	if (numOfGames == 0):
		return "There are no games being played at the moment."
	elif (numOfGames == 1):
		return "There is one game being played at the moment." 
		# TODO return details of the game
	else:
		return "There are " + str(numOfGames) + " games being played at the moment." 
		# TODO return details of the games

def get_client_name(IPv4, port):
	for r_user in registered_users:
		if (r_user[1] == IPv4 and r_user[2] == port):
			return r_user[0]

def game_start(user, k):
	print()

def game_end(game_id, user_dealer):
	print()

# Server setup
serverPort = 6250
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

# Global Variables
registered_users = []
concurrent_games = []


print("The server is ready to receive")
while True:
	# UDP messages have a max size of 2048 bytes
	# They all come in the form of strings sent by clients
	message, clientAddress = serverSocket.recvfrom(2048)
	# modifiedMessage = message.decode()

	# These messages sent by clients are in the form of commands
	# They are seperated by spaces
	# 'command_name' 'command_field1' ....
	command = tuple(map(str, message.decode().split(' ')))

	if   (command[0] == "register"):
		serverSocket.sendto( register(command[1], clientAddress[0], clientAddress[1]).encode(), clientAddress )
	# user exits and will de-register them
	elif (command[0] == "exit"):
		serverSocket.sendto( de_register(get_client_name(clientAddress[0], clientAddress[1])).encode(), clientAddress )
	elif (command[0] == "query"):
		if   (command[1] == "players"):
			serverSocket.sendto( query_players().encode(), clientAddress)
		elif (command[1] == "games"):
			serverSocket.sendto( query_games().encode(), clientAddress)
		else:
			serverSocket.sendto("INVALID COMMAND: " + message, clientAddress)
	else:
		serverSocket.sendto("INVALID COMMAND: " + message, clientAddress)