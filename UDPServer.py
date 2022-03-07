from gc import collect
import sys
from socket import *
import pickle
sys.path.append(".")

from CardGame import *

# Server setup
serverPort = 6250
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

# Global Variables
registered_users = []
concurrent_games = []
global game_id # no time to figure out how to implement static variables in python
game_id = 0
# this function takes 3 arguements: str user, str IPv4, int port
# It creates a new user to append to registeredUsers by default
# if a Username already exists, then it returns "FAILURE" and the server sends
# a message back to the client
# If a user tries to register another name, it will change their own Username
# however, this puts them at the end of the list, registeredUsers. 
def register(user, IPv4, port):
	# Our Player class is used to store the data of each user
	new_user = Player(user, IPv4, port)


	for r_user in registered_users:
		# If a user with the same name already exists
		if (r_user.name == user):
			return ("FAILURE", None)
		# Used for renaming a user on the same connection
		elif (r_user.IPv4 == IPv4 and r_user.port == port):
			r_user.name = user
			return ("SUCCESS", r_user)

	# create and append the new user
	registered_users.append(new_user)

	return ("SUCCESS", new_user)

# This function takes one argument, str user
# As long as that user is not in a game, it will de-register them
# returns "SUCCESS" on a removal, and "FAILURE" when it can't find the specific user
def de_register(user):
	for r_user in registered_users:
		if (r_user.name == user):
			registered_users.remove(r_user)
			print("De-registering: " + r_user.name + ".")
			return "SUCCESS"

	return "FAILURE"

# This function takes all the users in registeredUsers
# and returns a string in the form of 'username': 111.222.333:00000
def query_players():
	players = ""
	for r_user in registered_users:
		players += (r_user.name + ": " + r_user.IPv4 + ":" + str(r_user.port) + "\n")
	return ("SUCCESS", players)

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
		if (r_user.IPv4 == IPv4 and r_user.port == port):
			return r_user.name

def get_client_info(username):
	for r_user in registered_users:
		if (r_user.name == username):
			return r_user

def game_start(user_dealer, k):
	if (user_dealer == "" or k < 1 or k > 3):
		print("cant start game: dealer unspecific or invalid k value.")
		return ("FAILURE", [])
	else:
		# take the 1st k available players in registered_users and also 'user'
		# and send them the IP's of the others players so they know which sockets to send messages to.
		# The order of these IP's are: Dealer('user'), 1st available user, ..., k-th available user
		# toggle isInAGame on user and the k user(s)
		collected_players = []
		filtered_players = []

		collected_players.append( user_dealer )

		for user in registered_users:
			if (user != user_dealer and len(collected_players) < k + 1 and user.isInAGame == False):
				collected_players.append(user)
		print("CP: " + str(len(collected_players)) + " | k+1: " + str(k+1) )
		if (len(collected_players) < k + 1):
			print("cant start game: not enough players in queue")
			return ("FAILURE", [])
		for players in collected_players:
			# There are enough players to start a game
			# Set the current player to be in a game
			players.isInAGame = True
			# Send each player a message with the IP's of the other players
			if players != user_dealer:
				filtered_players = [player for player in collected_players if player != players]
				print(filtered_players)
				serverSocket.sendto(  pickle.dumps(("enter_game", filtered_players)), (players.IPv4, players.port) )
				
				message2, clientAddress = serverSocket.recvfrom(8192)
				print (message2 + " from " + clientAddress[0] + ":" + str(clientAddress[1]) )

		print("starting game with " + str(k+1) + " players with " + user_dealer.name + " as the dealer.")
		# create a new game 
		
		new_game = Game(game_id, user_dealer, collected_players)
		return ("SUCCESS", new_game)

def game_end(game_idd, user_dealer):
	# The dealer sends a message to the manager that the game has ended
	# In this message, the dealer sends the game_id in the message
	# The manager will check the ID of the game along and compare it's dealer info with 'user_dealer'
	# if they match, the game ends, the players in the game will no longer be marked inAGame
	# outcome of the game is printed to the console
	return



print("The server is ready to receive")
while True:
	# UDP messages have a max size of 8192 bytes
	# They all come in the form of strings sent by clients
	message, clientAddress = serverSocket.recvfrom(8192)
	# modifiedMessage = message.decode()

	# These messages sent by clients are in the form of commands
	# They are seperated by spaces
	# 'command_name' 'command_field1' ....
	command = tuple(map(str, message.decode().split(' ')))

	if (command[0] == "register" or command[0] == "r"):
		# serverSocket.sendto( register(command[1], clientAddress[0], clientAddress[1]).encode(), clientAddress )
		serverSocket.sendto( pickle.dumps(register(command[1], clientAddress[0], clientAddress[1])), clientAddress)
	# user exits and will de-register them
	elif (command[0] == "exit"):
		serverSocket.sendto( de_register(get_client_name(clientAddress[0], clientAddress[1])).encode(), clientAddress )
	elif (command[0] == "query"):
		if   (command[1] == "players"):
			# serverSocket.sendto( query_players().encode(), clientAddress)
			serverSocket.sendto( pickle.dumps(query_players()), clientAddress)
		elif (command[1] == "games"):
			serverSocket.sendto( query_games().encode(), clientAddress)
		else:
			serverSocket.sendto("INVALID COMMAND: " + message, clientAddress)
	elif (command[0] == "start"):
		serverSocket.sendto( pickle.dumps( game_start(get_client_info(get_client_name(clientAddress[0], clientAddress[1])), int(command[1]))), clientAddress ) 
	else:
		serverSocket.sendto("INVALID COMMAND: " + message, clientAddress)
