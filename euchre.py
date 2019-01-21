import random

EUCHRE_DECK = ['as', 'ks', 'qs', 'js', '10s', '9s', '8s',
               'ah', 'kh', 'qh', 'jh', '10h', '9h', '8h',
               'ad', 'kd', 'qd', 'jd', '10d', '9d', '8d',
               'ac', 'kc', 'qc', 'jc', '10c', '9c', '8c']

class RulesError(Exception):
    pass

class Player(object):
    def __init__(self, name):
        super(Player, self).__init__()
        self.hand = []
        self.name = name

    def draw(self, card):
        if len(self.hand) >= 5:
            raise RulesError("Player can't have more than 5 cards")
        elif card in self.hand:
            raise RulesError("Player can't have multiple of the same card")
        else:
            self.hand.append(card)

    def play(self, card):
        if card in self.hand:
            self.hand.remove(card)
        else:
            raise RulesError("Player can't play a card that isn't in their hand")


class EuchreGame(object):
    '''
    A class that represents a Euchre game.
    Typical game goes as follows:
    new_game()
    add_player('sam')
    add_player('gwyn')
    add_player('grace')
    add_player('ryan')


    '''
    def __init__(self):
        super(EuchreGame, self).__init__()
        # Reset after each game
        self.__points = [0, 0]
        self.__players = []
        self.__dealer = -1
        # Reset after each round
        self.__deck = None
        self.__first_bid_round = True
        self.__trumps = None
        self.__top_card = None
        self.__tricks = None
        self.__turn = None
        self.__current_trick = []
        self.__current_order = []
        self.__picked_trump = None

    def __set_turn(self, t):
        self.__turn = t % 4

    def __next_turn(self):
        self.__set_turn(self.__turn + 1)

    def __shuffle_deck(self):
        self.__deck = EUCHRE_DECK.copy()
        random.shuffle(self.__deck)

    def __deal(self):
        if len(self.__players) != 4:
            raise RulesError("Euchre can't start without 4 players")
        elif len(self.__deck) != len(EUCHRE_DECK):
            raise RulesError("Euchre can't start without 4 players")
        for i in range(20):
            self.__players[i % 4].draw(self.__deck.pop())
        self.__top_card = self.__deck.pop()

    @staticmethod
    def __card_ranking(led, trumps):
        if trumps not in ['s', 'h', 'd', 'c']:
            raise RulesError("Invalid trump suit in higher_card")
        elif led not in ['s', 'h', 'd', 'c']:
            raise RulesError("Invalid led suit in higher_card")
        ranking = ['j' + trumps]
        if trumps == 's':
            ranking.append('jc')
        elif trumps == 'c':
            ranking.append('js')
        elif trumps == 'h':
            ranking.append('jd')
        elif trumps == 'd':
            ranking.append('jh')
        for c in ['a', 'k', 'q', '10', ' 9', '8']:
            ranking.append(c + trumps)
        for c in ['a', 'k', 'q', 'j', '10', ' 9', '8']:
            ranking.append(c + led)

    def __evaluate_trick(self):
        led = self.__current_trick[0][-1]
        ranking = self.__card_ranking(led, self.__trumps)
        ranked_trick = []
        for card in self.__current_trick:
            if card in ranking:
                ranked_trick.append(ranked_trick.index(card))
            else:
                ranked_trick.append(999)
        winning_index = ranked_trick.index(min(ranked_trick))
        winner = self.current_order[winning_index]
        player_index = self.__players.index(winner)
        self.__tricks[player_index % 2] += 1
        self.__set_turn(player_index)
        self.__current_order = []
        return

    def __new_round(self):
        self.__dealer += 1
        self.__dealer %= 4
        self.__set_turn(self.__dealer + 1)
        self.__deck = None
        self.__first_bid_round = True
        self.__trumps = None
        self.__top_card = None
        self.__tricks = None
        self.__turn = None
        self.__current_trick = []
        self.__current_order = []
        self.__picked_trump = None
        self.__shuffle_deck()
        self.__deal()

    def __end_round(self):
        if self.__tricks[0] == 5 and self.__picked_trump == 1:
            self.__points[0] += 2
        elif self.__tricks[0] > 2:
            self.__points[0] += 1
        elif self.__tricks[1] == 5 and self.__picked_trump == 0:
            self.__points[1] += 2
        elif self.__tricks[1] > 2:
            self.__points[1] += 1
        else:
            raise RulesError('Tricks is in a bad configuration at the end of the round')
        self.__new_round()

    def new_game(self):
        '''
        Starts a new game
        :return: None
        '''
        self.__points = [0, 0]
        self.__players = []
        self.__dealer = -1
        self.__deck = None
        self.__trumps = None
        self.__top_card = None
        self.__tricks = None
        self.__turn = None
        self.__current_trick = []
        self.__picked_trump = None

    def add_player(self, name):
        '''
        Adds a palyer to the game
        :param name: str
            the name of the player
        :return: int [0,1,2,3]
            the index of the player
        '''
        if len(self.__players) < 4:
            self.__players.append(Player(name))
            if len(self.__players) == 4:
                self.__new_round()
            return len(self.__players) - 1
        else:
            raise RulesError("Euchre can't have more than 4 players")

    def bid(self, suit):
        '''
        Registers a bid for the current player
        :param suit:
        :return: int [0, 1, 2]
            next turn if the player passed, -1 if the player bid in the first round, -2 if the player bin in the second
        '''
        if suit == 'pass':
            if self.__turn == self.__dealer and self.__first_bid_round :
                self.__first_bid_round = False
            elif self.__turn == self.__dealer:
                raise RulesError("Dealer can't pass in the second round of bidding")
            self.__next_turn()
            return self.__turn
        elif self.__first_bid_round:
            if suit == 'top':
                self.__trumps = self.__top_card[-1]
                self.__picked_trump = self.__turn % 2
                self.__set_turn(self.__dealer + 1)
                return -1
            else:
                raise RulesError("In first round of bidding, you must pass or choose the top card")
        elif suit not in ['s', 'h', 'd', 'c']:
            raise RulesError("Invalid suit for second round of bidding. Must be one of: s, h, d, c")
        elif suit == self.__top_card[-1]:
            raise RulesError("Can't bid the same suit as the top card in the second round")
        else:
            self.__trumps = suit
            self.__picked_trump = self.__turn % 2
            self.__set_turn(self.__dealer + 1)
            return -2

    def dealer_draw_top_card(self, card):
        '''
        Discards a card from the dealer's hand, and adds the top card to their hand
        :param card: str
            the card to discard
        :return: None
        '''
        if self.__trumps is None:
            raise RulesError("Dealer can only pick up the top_card after trumps is set")
        elif self.__trumps != self.__top_card[-1]:
            raise RulesError("Dealer can only pick up the top_card after trumps is set")
        self.__players[self.__dealer].play(card)
        self.__players[self.__dealer].draw(self.__top_card)

    def play(self, card):
        '''
        Plays a card from the current palyer's hand
        :param card: str
            the card to play
        :return: int [0,1,2,3]
            the turn of the next player
        '''
        self.__players[self.__turn].play(card)
        self.__current_trick.append(card)
        self.__current_order.append(self.__players[self.__turn])
        self.__next_turn()
        if len(self.__current_trick) == 4:
            self.__evaluate_trick()
            if sum(self.__tricks) == 5:
                return self.__end_round()
        return self.__turn

    def game_state(self):
        '''
        Get a string representing the current game state
        :return: str
            a string with the current state and brackets for formatting name
        :return: list of str
            a lsit of the names for formatting
        '''
        names = []
        output = ''
        output += 'Points:\n'
        output += '{} and {}: ' + str(self.__points[0]) + '\n'
        names.append(self.__players[0].name)
        names.append(self.__players[1].name)
        output += '{} and {}: ' + str(self.__points[1])  + '\n\n'
        names.append(self.__players[2].name)
        names.append(self.__players[3].name)
        output += 'Tricks:\n'
        output += '{} and {}: ' + str(self.__tricks[0]) + '\n'
        names.append(self.__players[0].name)
        names.append(self.__players[1].name)
        output += '{} and {}: ' + str(self.__tricks[1])  + '\n\n'
        names.append(self.__players[2].name)
        names.append(self.__players[3].name)
        output += 'Current Trick:\n'
        for card in self.__current_trick:
            output += '{}: ' + card + '\n'
        for player in self.__current_order:
            names.append(player.name)
        return output, names

    def get_current_player(self):
        if self.__turn is None:
            return None
        return self.__players[self.__turn].name

    def current_player_state(self):
        '''
        Gets a string representing the state of the current player's hand
        :return: str
            a string representing the player's hand and what they have to do
        '''
        output = ''
        if self.__trumps is None:
            output += "It's your turn to bid!\n"
            output += 'Top card:\n'
            output += self.__top_card + '\n'
        else:
            output += "It's your turn to play!\n"
            output += 'Trumps:\n'
            output += self.__trumps + '\n'
        output += 'Your hand:\n'
        for card in self.__players[self.__turn].hand:
            output += card + ' '







