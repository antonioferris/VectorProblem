
class Card():
    def __init__(self, suits, gcd):
        self.pos = set(suits)
        self.gcd = gcd

    def is_not(self, suit):
        if suit in self.pos:
            self.pos.remove(suit)
            if len(self.pos) == 1:
                self.collapse_to(next(iter(self.pos)))

    def collapse_to(self, suit):
        self.gcd.grab(suit)
        self.pos = {suit}
    
    def is_singular(self):
        return len(self.pos) == 1

    def get_value(self):
        if not self.is_singular():
            return None
        return next(iter(self.pos))

    def __str__(self):
        return ''.join(map(str, self.pos)) + ' '

class GlobalCardCount(): # count the global cards to make sure only 4 of a suit exist
    def __init__(self, suits):
        self.counts = {}
        for s in suits:
            self.counts[s] = 4
        self.update = False
        self.empty = []

    def grab(self, suit):
        if self.counts[suit] <= 0:
            raise Contradiction('more than 4 ' + str(suit) + ' asserted to exist')
        
        self.update = True
        self.counts[suit] -= 1
        if self.counts[suit] == 0:
            self.empty.append(suit)


class Player():
    def __init__(self, name, suits, gcd):
        self.name = name
        self.gcd = gcd
        self.suits = suits
        self.cards = [Card(suits, gcd) for _ in range(4)]

    def has_no(self, suit): # assert that this player has at no copies of suit
        for card in self.cards:
            if card.get_value() == suit:
                raise Contradiction(self.name + ' incorrectly asserted to have no ' + str(suit))
            card.is_not(suit)

    def collapse_card(self, suit): # helper that finds a non-singular card and collapses it to suit
        for card in self.cards:
            if not card.is_singular() and suit in card.pos:
                card.collapse_to(suit)
                return True
        return False
        
    def has(self, suit): # assert that this player has at least 1 copy of suit
        already_has = any([card.get_value() == suit for card in self.cards])
        if already_has:
            return True
        else:
            success = self.collapse_card(suit)
            if not success:
                raise Contradiction(self.name + ' incorrectly asserted to have ' + str(suit))

    '''
        Find cases where the number of cards in the pool might force certain cards
        to collapse.  i.e. 1 suit 0 is left in the global pool, the the current player's 
        cards look like: 2 2 01 01
        We know that the cards cannot be 2 2 0 0 because there is only 1 suit 0 left in the pool,
        so the player's cards must be 2 2 0 01
    '''
    def collapse_globals(self):
        non_singular = sum([not card.is_singular() for card in self.cards])
        pos_suits = self.cards[-1].pos # All non-singular cards have the same pos
        for suit in pos_suits:
            number_filled = 0
            for s in pos_suits - {suit}: # the set of pos_suits with suit removed
                number_filled += self.gcd.counts[s]
            
            # if we can't fill our cards with the remaining cards of other suits,
            # then we must make up the different with this suit
            diff = non_singular - number_filled
            for i in range(diff):
                success = self.collapse_card(suit)
                if not success:
                    raise Contradiction(self.name + ' ran out of suit '  + str(suit) + ' during collapse_globals')
            if diff > 0:
                return True
        return False

    def give(self, suit): # give a card of suit to another player
        for card in self.cards:
            if card.get_value() == suit:
                self.cards.remove(card)
                return card
        for card in self.cards:
            if suit in card.pos:
                self.cards.remove(card)
                card.collapse_to(suit)
                return card
        raise Contradiction(self.name + ' incorrectly attempting to give ' + str(suit))

    def get(self, card):
        self.cards.insert(0, card)

    def no_more(self, suit): # assert that no more of suit exist, so superposed cards cannot collapse to suit
        for card in self.cards:
            if not card.is_singular():
                card.is_not(suit)

    def has_four(self, suit):
        cnt = 0
        for card in self.cards:
            if card.get_value() == suit:
                cnt += 1
        return cnt == 4


    def __str__(self):
        return self.name + ' : ' + ''.join(map(str, self.cards)) + '\n'

class Contradiction(Exception):
    pass

class IncorrectInput(Exception):
    pass

class Game():

    def __init__(self, player_names, verbose):
        if player_names == None:
            player_names = self.get_player_names()
        N = len(player_names)
        suits = list(range(N))
        self.gcd = GlobalCardCount(suits)
        self.players = {name : Player(name, suits, self.gcd) for name in player_names}
        self.verbose = verbose
        self.suits = suits

    def get_player_names(self):
        names = []
        while True:
            s = input('Please enter a player name (or enter to end)')
            if s == '':
                break
            names.append(s)
        return names


    def run_game(self):
        turn_num = 0
        players = list(self.players.keys())
        N = len(players)
        while True:
            if self.verbose:
                self.show()
            while True:
                try:
                    winner = self.run_turn(players[turn_num % N])
                    break
                except Contradiction as e:
                    print(e)
            turn_num += 1
            if winner != None:
                print()
                if isinstance(winner, Player):
                    winner = winner.name
                print(winner, 'wins')
                print('final information:')
                self.show()
                break

    def consistency_update(self):
        while self.gcd.update:
            self.gcd.update = False
            for player in self.players.values():
                for suit in self.gcd.empty:
                    player.no_more(suit)

            # check player globals for collapses
            for player in self.players.values():
                player.collapse_globals()
                if self.gcd.update: # skip to the update process if a player collapses
                    break


    def run_turn(self, player):
        while True:
            s = input(player + ', please enter the player you asked, the suit, and the answer:\n$ ')
            print()
            if s == '':
                return 'No one'
            elif s == 'p':
                self.show()
                continue
            try:
                if len(s) == 3:
                    other, suit, ans = list(s)
                else:
                    try:
                        other, suit, ans = s.split()
                    except ValueError:
                        raise IncorrectInput('3 space-seperated values not entered')
                if other not in self.players.keys():
                    raise IncorrectInput('player specified not in game')
                if other == player:
                    raise IncorrectInput('Choose another player, not yourself')
                suit = int(suit)
                if not suit in self.suits:
                    raise IncorrectInput('suit specified not in game')
                if ans.lower() not in {'y', 'n'}:
                    raise IncorrectInput('answer specified must be y or n')
                ans = True if ans.lower() == 'y' else False
                break
            except IncorrectInput as e:
                print(e)

        
        self.players[player].has(suit)
        if ans: # transfer card from 1 player to another
            card = self.players[other].give(suit)
            self.players[player].get(card)
        else:
            self.players[other].has_no(suit)

        self.consistency_update()

        # WIN CONDITION 1
        if len(self.gcd.empty) == len(self.players):
            return player # All cards are accounted for, so the current player was won

        # WIN CONDITION 2
        for player in self.players.values():
            for suit in self.suits:
                if player.has_four(suit):
                    return player # player has 4 of a suit, so they have won
        return None

    def show(self): 
        print('Global Counts: ', self.gcd.counts)
        print(''.join(map(str, self.players.values())))


def main():
    players = ['a', 'b', 'c']
    game = Game(player_names=None, verbose=False)
    game.run_game()

if __name__ == '__main__':
    main()