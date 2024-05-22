class State:

    def __init__(self):
        self.exits = []

    def enter(self):
        pass

    def transit(self):
        pass

    def add_transit(self, _exit):
        self.exits.append(_exit)

    def has_transit(self, _exit):
        return _exit in self.exits


class StateMachine:
    def __init__(self):
        self.states = None

    def initial_state(self, state):
        self.state = state

    def transition(self, new_state):
        if self.state.has_transit(new_state):
            self.state.transit()
            new_state.enter()
            self.state = new_state
