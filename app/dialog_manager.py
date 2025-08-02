import json

class DialogState:
    def __init__(self):
        self.goal = None
        self.slots = {} # dict of key being the additional info required to reach goal and value being that info itself
        self.missing_slots = {}
        self.current_location = [0, 0] # default point of departure
        self.history = [] # keeps track of user input and system replies to provide context to llm
        self.reply_context = {} # context for llm when responding to user, mostly the returned data from entur api

    def log_turn(self, user_input, system_reply):
        self.history.append({"role": "user", "text": user_input})
        self.history.append({"role": "system", "text": system_reply})
    
    def to_dict(self): # convert the dialog state to a dict for easier access 
        return {
            "goal": self.goal,
            "slots": self.slots,
            "missing_slots": self.missing_slots,
            "current_location": self.current_location,
            "history": self.history,
            "reply_context": self.reply_context
        }
    
    def to_json(self): # to be used in llm prompt
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def is_ready(self): # ready meaning the necessary info required to perform api requests are provided
        return len(self.missing_slots) == 0