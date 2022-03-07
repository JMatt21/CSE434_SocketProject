from socket import *
import atexit # for exit_handler() and atexit.register
import sys
import pickle
from time import sleep
sys.path.append(".")
from CardGame import *

serverName = '129.219.10.241'
serverPort = 6250
clientSocket = socket(AF_INET, SOCK_DGRAM)

coopClients = []
dealerCardGame = None
player_info = None

# de-registers the user upon exit, whether through
# the exit command or by keyboard interrupt 
def exit_handler():
	print("bye bye")
	clientSocket.sendto("exit".encode(),(serverName, serverPort))
	clientSocket.close()

atexit.register(exit_handler)

def listen():
	while (True):
		global player_info
		global coopClients
		message, address = clientSocket.recvfrom(8192)
		message = pickle.loads(message)
		if (message[0] == "turn_start"):
			player_action()
		elif (message[0] == "get_hand"):
			clientSocket.sendto( pickle.dumps(("SUCCESS", player_info.get_hand())), address)
		elif (message[0] == "deal_hand"):
			player_info.hand = message[1]
		elif (message[0] == "steal"):
			# the message is in the form of 'steal' card# CardObject
			message[2].isFaceUp = True
			old_card = player_info.swap(message[2], message[1])
			clientSocket.sendto( pickle.dumps(("SUCCESS", old_card)), address)
		elif (message[0] == "hole_over" and address == coopClients[0].address):
			clientSocket.sendto( pickle.dumps(player_info), address)
		elif (message[0] == "enter_game"):
			print("GAME STARTING!!!")
			coopClients = message[1]
			clientSocket.sendto("SUCCESS".encode(), (serverName, serverPort))
		elif (message[0] == "peek_discard" and player_info.isDealer):
			clientSocket.sendto( ("The card on the discard pile is " + dealerCardGame.discard[len(dealerCardGame.discard) - 1].print_card() + ".").encode(), address )
		elif (message[0] == "draw_from_deck" and player_info.isDealer):
			clientSocket.sendto( pickle.dumps( ('SUCCESS', dealerCardGame.deck.pop()) ), address)
			dealerCardGame.discard.append(message[1])
		elif (message[0] == "draw_from_discard"):
			clientSocket.sendto( pickle.dumps( ('SUCCESS', dealerCardGame.discard.pop()) ), address)
			dealerCardGame.discard.append(message[1])
		elif (message[0] == "replace_drawn_card"):
			dealerCardGame.discard.append(message[1])
		elif (message[0] == "discard_drawn_card"):
			dealerCardGame.discard.append(message[1])
		elif (message[0] == "scores"):
			if (address == coopClients[0].address):
				for player in message[1]:
					print("Score this hole: " + player.get_score())
					print("Total Score: " + player.TotalScore)
					print(player.name + "'s hand: ")
					print(player.get_hand())

				clientSocket.sendto("ACK".encode(), address)
				player_info.hand = []

		elif (message[0] == "hole_finished" and player_info.isDealer):
			scores = []
			leaderScore = 0
			leaderName = []
			scores.append(player_info)
			# send a message to every client to get there scores
			for player in coopClients:
				if (player != message[1]):
					clientSocket.sendto( pickle.dumps("hole_over"), player.address)
					returned_message, address = clientSocket.recvfrom(8192)
					scores.append( pickle.loads((returned_message[1])) )
			# send the scores to every client and await an ACK
			for player in coopClients:
				clientSocket.sendto( pickle.dumps("scores", scores), player.address)
				returned_message, address = clientSocket.recvfrom(8192)
				print(player.name + " " + returned_message.decode())
			
			for player in scores:
				player.TotalScore += player.get_score()
				if (player.TotalScore < leaderScore):
					leaderScore == player.TotalScore
					leaderName.clear()
					leaderName.append(player.name)
				elif (player.TotalScore == leaderScore):
					leaderName.append(player.name)
			dealerCardGame.players = scores

			

			if (dealerCardGame.roundNumber <= dealerCardGame.maxRounds):
				# start another round
				dealerCardGame.generate_new_shuffled_deck()
				dealerCardGame.start_game()
				player_action()
		 

def player_action():
	currently_taking_an_action = True
	while (currently_taking_an_action):
		print("Your Hand:")
		print(player_info.get_hand())
		message = raw_input('Type a command here: ') # raw_input is used because general2 is running python 2.7.5
		command = tuple(map(str, message.split(' ')))
		if (command[0] == "peek"):
			if (command[1] == "discard"):
					if (player_info.isDealer):
						print("The card on the discard pile is " + dealerCardGame.discard[len(dealerCardGame.discard) - 1].print_card() + ".")
					else:
						clientSocket.sendto( pickle.dumps(("peek_discard", ' ')), coopClients[0].address)
						returned_message, address = clientSocket.recvfrom(8192)
						returned_message = pickle.loads(returned_message)
						if (returned_message[0] == "SUCCESS"):
							print("The card on the discard pile is " + returned_message[1].print_card() + ".")
						# if (returned_message[0] == "FAILURE"):
						# 	print("Something went wrong")
				
			else:
				# e.g. peek randy
				# getPlayer uses a filter to grab a specific player out of dealerCardGame.players
				# the user has already been pop'd out of coopClients
				# so there is no need to check to see if the dealer is trying to peek at theirself.
				getPlayer = [player for player in coopClients if player.name == command[1]][0]
				if (getPlayer != None):
					clientSocket.sendto( pickle.dumps(('get_hand', '')) , getPlayer.address )
					returned_message, address = clientSocket.recvfrom(8192)
					returned_message = pickle.loads(returned_message)
					print("Hand from: " + getPlayer.name)
					print(returned_message[1])
				else:
					print("Player " + command[1] + " not found.")
		elif (command[0] == "draw"):
			if (command[1] == "deck"):
				if(player_info.isDealer):
					new_card = dealerCardGame.deck.pop() # pop a card from the stack
				else:
					clientSocket.sendto( pickle.dumps(("draw_from_deck", '')), coopClients[0].address)
					returned_message, address = clientSocket.recvfrom(8192)
					returned_message = pickle.loads(returned_message)
					if (returned_message[0] == "SUCCESS"):
						new_card = returned_message[1]
				
				new_card.isFaceUp = True
				
				print("The card from the deck is a " + new_card.print_card() + ".")

				while (currently_taking_an_action):			
					message = raw_input('Replace a card (1-6) or discard?: ') # raw_input is used because general2 is running python 2.7.5
					command = tuple(map(str, message.split(' ')))

					if (command[0] == "discard"):
						if(player_info.isDealer):
							dealerCardGame.discard.append(new_card)
						else:
							clientSocket.sendto( pickle.dumps(("discard_drawn_card", new_card)), coopClients[0].address)					
					
					else:
						old_card = player_info.swap(new_card, int(command[0]) - 1)

						if (player_info.isDealer):
							dealerCardGame.discard.append(old_card)
						else:
							clientSocket.sendto( pickle.dumps(("replace_drawn_card", old_card)), coopClients[0].address)
					currently_taking_an_action = False

			elif (command[1] == "discard"):
				if (player_info.isDealer):
					new_card = dealerCardGame.discard.pop() # pop a card from the stack
				else:
					clientSocket.sendto( pickle.dumps(("draw_from_discard", '')), coopClients[0].address)
					returned_message, address = clientSocket.recvfrom(8192)
					returned_message = pickle.loads(returned_message)
					if (returned_message[0] == "SUCCESS"):
						new_card = returned_message[1]

				print("The card from the discard pile is a " + new_card.print_card() + ".")

				while (currently_taking_an_action):
					index = raw_input('Replace a which card (1-6)?: ') # raw_input is used because general2 is running python 2.7.5
					if (type(int(index)) != int or index > 6 or index < 1):
						print("Invalid Input")
					elif (player_info.isDealer):
						old_card = player_info.swap(new_card, index - 1)
						dealerCardGame.discard.append()
					elif (player_info.isDealer == False):
						old_card = player_info.swap(new_card, index - 1)
						clientSocket.sendto( pickle.dumps(("discarding", old_card)), coopClients[0].address)
						
					currently_taking_an_action = False
		# e.g. steal 3 from randy replace 2
		elif (command[0] == "steal" and command[2] == "from" and command[4] == "replace"):
			if (type(command[1]) != int or type(command[5]) != int or command[1] > 6 or command[1] < 1 or command[5] > 6 or command[5] < 1):
				print("Invalid Input ")
			elif (player_info.hand[command[5]].isFaceUp):
				print("You must replace a face down card.")
			else:
				selectedPlayer = coopClients.players[coopClients.players.index(command[3])]
				
				clientSocket.sendto( pickle.dumps(("steal", command[1], player_info.hand[command[5]])), (selectedPlayer.IPv4, selectedPlayer.port) )
				returned_message, address = clientSocket.recvfrom(8192)
				returned_message = pickle.loads(returned_message)
				returned_message[1].isFaceUp = True
				player_info.hand[command[5]] = returned_message[1]
				currently_taking_an_action = False



		elif (command[0] == "players"):
			print("Other Players: ")
			for player in coopClients:
				print (player.name)
		else:
			print("Invalid Command.")
			

	holeOver = player_info.is_hole_filled()
	if (holeOver):
		if(player_info.isDealer):
			scores = []
			leaderName = []
			leaderScore = 123123123
			scores.append(player_info)
			# send a message to every client to get there scores
			for player in coopClients:
				clientSocket.sendto( pickle.dumps(("hole_over", ' ')), player.address)
				returned_message, address = clientSocket.recvfrom(8192)
				scores.append( pickle.loads((returned_message[1])) )
			# send the scores to every client and await an ACK
			for player in coopClients:
				clientSocket.sendto( pickle.dumps(("scores", scores)), player.address)
				returned_message, address = clientSocket.recvfrom(8192)
				print(player.name + " " + pickle.loads(returned_message[0])) 

			for player in scores:
				player.TotalScore += player.get_score()
				if (player.TotalScore < leaderScore):
					leaderScore == player.TotalScore
					leaderName.clear()
					leaderName.append(player.name)
				elif (player.TotalScore == leaderScore):
					leaderName.append(player.name)
			dealerCardGame.players = scores



			if (dealerCardGame.roundNumber <= dealerCardGame.maxRounds):
				# start another round
				dealerCardGame.generate_new_shuffled_deck()
				dealerCardGame.start_game()
				player_action()
			else:

				for player in coopClients:
					clientSocket.sendto(pickle.dumps( ('game_over', leaderName, leaderScore) ))

		else:
			clientSocket.sendto( pickle.dumps(("hole_filled", player_info)), coopClients[0].address)
			returned_message, address = clientSocket.recvfrom(8192)
			returned_message = pickle.loads(returned_message)
			if (returned_message[0] == "SUCCESS"):
				for player in scores:
					print("Score this hole: " + player.get_score())
					print("Total Score: " + player.TotalScore)
					print(player.name + "'s hand: ")
					print(player.get_hand())
	else:

		print("Turn Complete, waiting for other players...")
		sleep(.25)
		print("Your Hand:")
		print(player_info.get_hand())
		clientSocket.sendto( pickle.dumps(("turn_start", ' ')), coopClients[0].address)
		listen()



while (True):
		message = raw_input('Type a command here: ') # raw_input is used because general2 is running python 2.7.5
		command = tuple(map(str, message.split(' ')))

		if (command[0] == "l"):
			listen()
		elif (command[0] == "query" and command[1] == "players"):
			clientSocket.sendto(message.encode(), (serverName, serverPort))
			returned_message, serverAddress = clientSocket.recvfrom(8192)
			returned_message = pickle.loads(returned_message)

			print  (returned_message[1])
		elif (command[0] == "query" and command[1] == "games"):
			clientSocket.sendto(message.encode(), (serverName, serverPort))
			returned_message, serverAddress = clientSocket.recvfrom(8192)

			print(returned_message.decode())
		else: 
			clientSocket.sendto(message.encode(), (serverName, serverPort))

			returned_message, serverAddress = clientSocket.recvfrom(8192)

			if (command[0] == "exit"):
				exit()
			elif (command[0] == "start"):
				returned_message = pickle.loads(returned_message)
				if (returned_message[0] == "SUCCESS"):
					# the server sends back a 'Game' object
					dealerCardGame = returned_message[1]
					player_info = dealerCardGame.user_dealer

					coopClients = dealerCardGame.players[1:len(dealerCardGame.players)]
					
					new_hand = []
					sleep(1)
					for x in range(6):
							new_card = dealerCardGame.deck.pop()
							if (x < 2):
								new_card.isFaceUp = True
							player_info.hand.append( new_card )		
					for player in coopClients:
						print("SENDING")
						for x in range(6):
							new_card = dealerCardGame.deck.pop()
							if (x < 2):
								new_card.isFaceUp = True
							new_hand.append( new_card )	
						# send a message to each player their starting hand
						clientSocket.sendto( pickle.dumps(("deal_hand", new_hand)), player.address)
					dealerCardGame.discard.append( dealerCardGame.deck.pop() )
					print("Game Starting...")
					player_action()
			elif (command[0] == "r" or command[0] == "register"):
				returned_message = pickle.loads(returned_message)
				if ( returned_message[0] == "SUCCESS"):
					player_info = returned_message[1]
					print(returned_message[0])
			else:
				print(returned_message.decode())