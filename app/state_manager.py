from dialog_manager import DialogState

session_states = {}

def get_state(session_id):
    if session_id in session_states:
        return session_states[session_id] # DialogState object
    else:
        state = DialogState()
        session_states[session_id] = state
        return state