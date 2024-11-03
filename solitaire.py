from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker
import pprint
import random

pp = pprint.PrettyPrinter(indent=4)


class Game:
    VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    COLORS = ["red", "black"]
    SUITS = {u'\u2660': "black", u'\u2665': "red", u'\u2663': "black", u'\u2666': "red"}
    NUM_PLAY_PILES = 7

    def __init__(self):
        self.deck = Deck(self.VALUES, self.SUITS)
        self.play_piles = [self._create_pile(i) for i in range(self.NUM_PLAY_PILES)]
        self.block_piles = {suit: Pile() for suit in self.SUITS}
        self.deck.cards[0].flip()

    def _create_pile(self, num_cards):
        pile = Pile()
        for _ in range(num_cards + 1):
            pile.addCard(self.deck.takeFirstCard(flip=False))
        pile.flipFirstCard()
        return pile

    def get_game_elements(self):
        return {
            "deck": str(self.deck),
            "playPiles": [str(pile) for pile in self.play_piles],
            "blockPiles": {suit: str(pile) for suit, pile in self.block_piles.items()}
        }

    def check_card_order(self, higher_card, lower_card):
        suits_different = self.SUITS[higher_card.suit] != self.SUITS[lower_card.suit]
        value_consecutive = self.VALUES[self.VALUES.index(higher_card.value) - 1] == lower_card.value
        return suits_different and value_consecutive

    def check_if_completed(self):
        return (
            len(self.deck.cards) == 0 and
            all(len(pile.cards) == 0 for pile in self.play_piles) and
            all(len(pile.cards) == 13 for pile in self.block_piles.values())
        )

    def add_to_block(self, card):
        if card is None:
            return False
        pile = self.block_piles[card.suit]
        if pile.cards and self.VALUES[self.VALUES.index(pile.cards[0].value) + 1] == card.value:
            pile.cards.insert(0, card)
            return True
        elif card.value == "A":
            pile.cards.insert(0, card)
            return True
        return False

    def take_turn(self, verbose=False):
        for pile in self.play_piles:
            if pile.cards and self.add_to_block(pile.cards[0]):
                pile.cards.pop(0)
                if verbose:
                    print(f"Adding play pile card to block: {pile.cards[0]}")
                return True
        if self.add_to_block(self.deck.getFirstCard()):
            if verbose:
                print(f"Adding card from deck to block: {self.deck.takeFirstCard()}")
            return True
        return False

    def simulate(self, max_steps=500, verbose=False):
        steps = 0
        self.deck.cache = []
        while steps < max_steps:
            steps += 1
            turn_result = self.take_turn(verbose=verbose)
            
            if not turn_result:
                # Attempt to draw from the deck if no turn result is achieved
                if len(self.deck.cards) > 0:
                    current_card = self.deck.cards[0]
                    
                    # Check if this card has already been seen (avoiding endless loops)
                    if current_card in self.deck.cache:
                        print(f"Ending: Deck cycling detected. No new moves at step {steps}.")
                        break
                    else:
                        # Draw a new card and continue simulation
                        self.deck.drawCard()
                        self.deck.cache.append(current_card)
                        if verbose:
                            print(f"Drawn card: {current_card}")
                else:
                    # No cards left to draw, end the game
                    print(f"Ending: Deck is empty with no further moves at step {steps}.")
                    break
        else:
            print("Simulation ended after reaching max steps without completion.")

    def bogosort(self):
        arr_values = [card.value for card in self.deck.cards]
        while not all(arr_values[i] <= arr_values[i + 1] for i in range(len(arr_values) - 1)):
            random.shuffle(arr_values)
        sorted_cards = [Card(value, suit) for value, suit in zip(arr_values, [card.suit for card in self.deck.cards])]
        self.deck.cards = sorted_cards
        print("Sorted Cards:")
        for card in sorted_cards:
            print(card)


def main():
    with EmissionsTracker() as tracker:
        game = Game()
        game.simulate(verbose=True)
        print("\nGame Elements:")
        pp.pprint(game.get_game_elements())
        if game.check_if_completed():
            print("Congrats! You won!")
        else:
            print("Sorry, you did not win")
        game.bogosort()


main()
