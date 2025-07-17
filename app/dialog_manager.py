import openai

class DialogState: # 
    def __init__(self):
        self.goal = None
        self.slots = {}
        self.missing_slots = {}
        self.current_location = [0, 0] # default point of departure
        self.history = []

    def update_slot(self, slot, value):
        self.slots[slot] = value
        self.missing_slots = [ # to contain remaining slots required to reach goal
            k for k, v in self.slots if v == None
        ]

    def is_ready(self):
        return len(self.missing_slots) == 0