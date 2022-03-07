import random # for shuffling

suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
card_values = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

class Card:
	def __init__(self, value, suit):
		# tried to use private varaibles but couldn't get it to work
		# trusting the UDPClient to not change values
		self.value = value
		self.suit = suit
		self.card_text = value[0] + suit[0]
		self.isFaceUp = False
		
	def get_score(self):
		if (self.value == "Ace"):
			return 1
		elif (self.value == "2"):
			return -2
		elif (self.value == "Jack" or self.value == "Queen"):
			return 10
		elif (self.value == "King"):
			return 0
		else:
			return int(self.value)
			
	def print_card(self):
		return self.value + " of " + self.suit
	def out(self):
		if (self.isFaceUp):
			if (self.value != '10'): 
			# because of the 'hand printing' requirements, cards with a value of '10'
			# need special treatment becuase the other cards have to be printed with 
			# a space behind the value, instead of infront of the suit
				return " " + self.card_text
			return self.card_text
		else:
			return "***"		

class Player:
	def __init__(user, name, IPv4, port):
		user.name = name
		user.IPv4 = IPv4
		user.port = port
		user.isInAGame = False
		user.hand = []
		user.address = (IPv4, port)
		user.isDealer = False
		user.order = 0
		user.TotalScore = 0

	def out(user):
		return user.name + ", " + user.IPv4 + ":" + user.port
	def get_hand(user):
		return user.hand[0].out() + " " + user.hand[1].out() + " " + user.hand[2].out() + "\n" + user.hand[3].out() + " " + user.hand[4].out() + " " + user.hand[5].out()
	def swap(user, new_card, old_card_index):
		old_card = user.hand[old_card_index]
		user.hand[old_card_index] = new_card
		return old_card
	def get_score(user):
		score = 0
		for card in user.hand:
			score += card.getScore()

		i = 0
		while(i < 3):
			if (user.hand[i].getScore() == user.hand[i+2].getScore()):
				score -= (user.hand[i].getScore * 2)


			
		return score
	def is_hole_filled(user):
		ret = True
		for card in user.hand:
			if (card.isFaceUp != True):
				ret = False
		return ret

	def flip_cards_over(user):
		for card in user.hand:
			card.isFaceUp = True


class Game:
	def __init__(self, id, user_dealer, players):
		self.deck = [] # functions as a stack
		self.discard = [] # functions as a stack
		self.players = players # first index is the dealer, 
						  # 2nd player is on the dealers left and so on
		self.user_dealer = user_dealer
		self.id = id

		self.user_dealer.isDealer = True
		self.roundNumber = 1
		self.maxRounds = 2
		# generate a deck of cards
		for suit in suit_names:
			for value in card_values:
				new_card = Card(value, suit)
				self.deck.append(new_card)

		# shuffle the deck
		random.shuffle(self.deck)

	def deal_cards(self):
		new_hand = []
		dealers_hand = []
		for x in range(6):
				dealers_hand.append( self.deck.pop() )	
		for player in self.players:
			if (player != self.user_dealer):
				for x in range(6):
					new_hand.append( self.deck.pop() )	
					# send a message to each player their starting hand
					
		
		return dealers_hand
			

	def start_game(self):
		self.deal_cards()
		# flip a card from the deck onto the discard pile
		self.discard.append( self.deck.pop() )
	
	def generate_new_shuffled_deck(self):
		# simulate the gathering of all the cards
		# by deleting every single card
		# cards owned by players will be replaced
		# from deal_cards()
		self.deck = []
		self.discard = []
		self.roundNumber += 1
		# generate a deck of cards
		for suit in suit_names:
			for value in card_values:
				new_card = Card(value, suit)
				self.deck.append(new_card)
		# shuffle the deck
		random.shuffle(self.deck)


