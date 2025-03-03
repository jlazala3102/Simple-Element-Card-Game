# card.py

class Card:
    def __init__(self, card_type):
        self.type = card_type

    def __str__(self):
        return self.type
