from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker
import pprint
import random

# Initialize pretty printer for cleaner output
pp = pprint.PrettyPrinter(indent=4)

# Start tracking emissions
with EmissionsTracker() as tracker:

    class Game:
        # Define class-level attributes for suits and values
        suits = {
            'Diamonds': "red",
            'Hearts': "red",
            'Clubs': "black",
            'Spades': "black"
        }
        values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        numPlayPiles = 7

        def __init__(self):
            # Pass values and suits to Deck
            self.deck = Deck(self.values, list(self.suits.keys()))
            self.playPiles = [self._create_pile(i) for i in range(self.numPlayPiles)]
            self.blockPiles = {suit: Pile() for suit in self.suits}
            self.deck.cards[0].flip()

        def _create_pile(self, count):
            # Helper to initialize piles with specified cards
            pile = Pile()
            for _ in range(count + 1):
                pile.addCard(self.deck.takeFirstCard(flip=False))
            pile.flipFirstCard()
            return pile

        def getGameElements(self):
            # Return game elements for inspection
            return {
                "deck": str(self.deck),
                "playPiles": [str(pile) for pile in self.playPiles],
                "blockPiles": {suit: str(pile) for suit, pile in self.blockPiles.items()}
            }

        def checkCardOrder(self, higherCard, lowerCard):
            # Checks if the cards are in correct order
            return (
                self.suits[higherCard.suit] != self.suits[lowerCard.suit]
                and self.values[self.values.index(higherCard.value) - 1] == lowerCard.value
            )

        def checkIfCompleted(self):
            # Check if the game is completed
            return (
                len(self.deck.cards) == 0
                and all(len(pile.cards) == 0 for pile in self.playPiles)
                and all(len(pile.cards) == 13 for pile in self.blockPiles.values())
            )

        def addToBlock(self, card):
            # Optimized check to add cards to block pile
            if not card:
                return False
            block_pile = self.blockPiles[card.suit]
            if block_pile.cards and self.values[self.values.index(block_pile.cards[0].value) + 1] == card.value:
                block_pile.cards.insert(0, card)
                return True
            elif not block_pile.cards and card.value == "A":
                block_pile.cards.insert(0, card)
                return True
            return False

        def takeTurn(self, verbose=False):
            # Flip unflipped pile cards automatically
            for pile in self.playPiles:
                if pile.cards and not pile.cards[0].flipped:
                    pile.cards[0].flip()

            # Process actions based on game rules
            actions = [
                (self._movePlayPileCardToBlock, "Moved play pile card to block"),
                (self._moveDeckCardToBlock, "Moved deck card to block"),
                (self._moveKingToOpenPile, "Moved King to empty pile"),
                (self._addDeckCardToPlayPile, "Added deck card to play pile"),
                (self._moveBetweenPlayPiles, "Moved cards between play piles"),
            ]
            for action, message in actions:
                if action(verbose):
                    if verbose:
                        print(message)
                    return True
            return False

        def _movePlayPileCardToBlock(self, verbose):
            # Check if play pile cards can be moved to block pile
            for pile in self.playPiles:
                if pile.cards and self.addToBlock(pile.cards[0]):
                    pile.cards.pop(0)
                    return True
            return False

        def _moveDeckCardToBlock(self, verbose):
            # Check if the top deck card can be moved to block pile
            card = self.deck.getFirstCard()
            if card and self.addToBlock(card):
                self.deck.takeFirstCard()
                return True
            return False

        def _moveKingToOpenPile(self, verbose):
            # Move King to any empty play pile
            for pile in self.playPiles:
                if not pile.cards:
                    for src_pile in self.playPiles:
                        if src_pile.cards and src_pile.cards[0].value == "K":
                            pile.addCard(src_pile.cards.pop(0))
                            return True
                    card = self.deck.getFirstCard()
                    if card and card.value == "K":
                        pile.addCard(self.deck.takeFirstCard())
                        return True
            return False

        def _addDeckCardToPlayPile(self, verbose):
            # Add drawn card to play pile if conditions match
            card = self.deck.getFirstCard()
            for pile in self.playPiles:
                if pile.cards and card and self.checkCardOrder(pile.cards[0], card):
                    pile.addCard(self.deck.takeFirstCard())
                    return True
            return False

        def _moveBetweenPlayPiles(self, verbose):
            # Move cards between play piles based on order rules
            for src_pile in self.playPiles:
                flipped_cards = src_pile.getFlippedCards()
                if flipped_cards:
                    for dest_pile in self.playPiles:
                        if dest_pile is not src_pile and dest_pile.cards:
                            for transfer_size in range(1, len(flipped_cards) + 1):
                                to_transfer = flipped_cards[:transfer_size]
                                if self.checkCardOrder(dest_pile.cards[0], to_transfer[-1]):
                                    dest_pile.cards[:0] = reversed(to_transfer)
                                    src_pile.cards = src_pile.cards[transfer_size:]
                                    return True
            return False

        def simulate(self, verbose=False):
            # Run simulation until completion
            while self.takeTurn(verbose):
                pass

        def bogosort(self):
            # Replace bogo sort with a more efficient sorting algorithm (merge sort here)
            self.deck.cards.sort(key=lambda card: (self.values.index(card.value), card.suit))

    # Main function to run the game
    def main():
        game = Game()
        game.simulate(verbose=True)
        print("\nGame Elements:")
        pp.pprint(game.getGameElements())
        if game.checkIfCompleted():
            print("Congrats! You won!")
        else:
            print("Sorry, you did not win")
        game.bogosort()
        print("Sorted cards:", [str(card) for card in game.deck.cards])

    main()
