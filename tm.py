"""
Module for simulating Turing machines.
"""

class Symbol(object):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "<%s>" % self.name.upper()

class State(Symbol):
    pass

class Letter(Symbol):
    pass

class Move(Symbol):
    pass

# Default alphabet:
START_A = Letter('start')
BLANK = Letter('blank')

# Default states:
QSTART = State('start')
HALT = State('halt')

# Movements
LEFT = Move('left')
STAY = Move('stay')
RIGHT = Move('right')

class Tape(object):
    def __init__(self, input_contents=[]):
        self._contents = [START_A] + input_contents
        self._position = 0
        self._negative_space = 0 # How far out into the negatives we've gone

    def read(self):
        return self._contents[self._position + self._negative_space]

    def write(self, val):
        self._contents[self._position + self._negative_space] = val

    def _expand_right(self):
        expansion = [BLANK] * len(self._contents)
        self._contents += expansion

    def _expand_left(self):
        expansion = [BLANK] * len(self._contents)
        self._contents = expansion + self._contents
        self._negative_space += len(expansion)

    def move(self, move):
        if move == STAY:
            return
        elif move == RIGHT:
            self._position += 1
            if self._position > (len(self._contents) - self._negative_space - 1):
                self._expand_right()
        elif move == LEFT:
            self._position -= 1
            if self._position < -self._negative_space:
                self._expand_left()
        else:
            raise ValueError("Unknown move %s" % move)

    def pprint(self):
        print ' '.join(map(str, self._contents))

def augment_default_alphabet(alphabet):
    alphabet = alphabet or []
    ret = set([START_A, BLANK, '0', '1'])
    for a in alphabet:
        assert isinstance(a, Letter) or isinstance(a, basestring) and len(a) == 1
        ret.add(a)
    return ret

def augment_default_states(states):
    states = states or []
    ret = set([QSTART, HALT])
    for s in states:
        assert isinstance(s, State) or isinstance(s, basestring) and len(s) == 1
        ret.add(s)
    return ret

class TuringMachine(object):
    def __init__(self, alphabet, states, transition_function, num_tapes=1):
        """
        `alphabet` is added to the default alphabet, which contains BLANK, START, 0, and 1
        `states` are added to the default states: START and HALT
        `transition_function` is f: (State, Alphabet^num_tapes) -> (State, Alphabet^num_tapes, {L, S, R}^k)
            The inputs and outputs that are dependent on number of tapes should be provided as tuples.
        """
        self._num_tapes = num_tapes
        self.alphabet = augment_default_alphabet(alphabet)
        self.states = augment_default_states(states)
        self.transition_function = transition_function
        self.current_state = QSTART

    def run_next_step(self):
        tape_values = tuple(t.read() for t in self.tapes)
        new_state, writes, moves = self.transition_function(self.current_state, tape_values)
        self.current_state = new_state
        assert len(writes) == len(self.tapes)
        for i, w in enumerate(writes):
            self.tapes[i].write(w)
        for i, m in enumerate(moves):
            self.tapes[i].move(m)

    def run(self):
        while self.current_state != HALT:
            self.run_next_step()

    def initialize(self, input_contents):
        self.tapes = [Tape() for x in range(self._num_tapes)]
        self.tapes[0] = Tape(input_contents)

    def run_on(self, input_contents):
        self.initialize(input_contents)
        self.run()

    def run_verbosely(self, input_contents):
        self.initialize(input_contents)
        while self.current_state != HALT:
            print '-'*20
            self.printall()
            self.run_next_step()
        print '-'*20
        self.printall()

    def printall(self):
        print "State:", self.current_state
        for i, t in enumerate(self.tapes):
            print "Tape %d:" % i
            t.pprint()

# 0. Go x until y, (writing z)
# 1. Go to end
# 2. Add 1
