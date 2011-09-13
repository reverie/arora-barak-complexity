import sys
import itertools

import tm

class PAL(object):
    COPY, LEFT, TEST = (tm.State(x) for x in ['copy', 'left', 'test'])

    @classmethod
    def transition(cls, state, inputs):
        # Tapes: input, work, output

        # Setup
        i1, i2, i3 = o1, o2, o3 = inputs
        m1, m2, m3 = tm.STAY, tm.STAY, tm.STAY
        new_state = state

        # Transitions, structured as the textbook presents them
        if state == tm.QSTART:
            m1 = m2 = tm.RIGHT
            new_state = cls.COPY
        elif state == cls.COPY:
            if i1 != tm.BLANK:
                m1 = m2 = tm.RIGHT
                o2 = i1 # Write input tape read to work tape
            else:
                m1 = tm.LEFT
                new_state = cls.LEFT
        elif state == cls.LEFT:
            if i1 != tm.START_A:
                m1 = tm.LEFT
            else:
                m1 = tm.RIGHT
                m2 = tm.LEFT
                new_state = cls.TEST
        elif state == cls.TEST:
            if i1 == tm.BLANK and i2 == tm.START_A:
                o3 = '1'
                new_state = tm.HALT
            elif i1 != i2:
                o3 = '0'
                new_state = tm.HALT
            else:
                m1 = tm.RIGHT
                m2 = tm.LEFT
        else:
            raise ValueError("Unknown state %s" % state)
        return new_state, (o1, o2, o3), (m1, m2, m3)

    @classmethod
    def make(cls):
        pass
        """
        Returns a TM for PAL as in Example 1.1
        """
        # Make TM
        extra_states = [cls.COPY, cls.LEFT, cls.TEST]
        return tm.TuringMachine(
            None, # Use default alphabet,
            extra_states,
            cls.transition,
            3) # Input, work, output

class ADDER(object):
    # General plan:
    # 1. Copy 2nd number to a work tape
    # 2. Go to last bits of both tapes
    # 3. Add with carry, moving left

    COPY, RIGHT, ADD, ADDCARRY = (tm.State(x) for x in ['copy', 'right', 'add', 'addcarry'])

    @classmethod
    def transition(cls, state, inputs):
        # Tapes: input, work, output

        # Setup
        i1, i2, i3 = o1, o2, o3 = inputs
        m1, m2, m3 = tm.STAY, tm.STAY, tm.STAY
        new_state = state

        if state == tm.QSTART:
            m1 = tm.RIGHT
            new_state = cls.COPY
        elif state == cls.COPY:
            if i1 != tm.BLANK:
                m1 = m2 = tm.RIGHT
                o2 = i1 # Write input tape read to work tape
            else:
                m1 = tm.RIGHT # Start going right to end of 2nd number
                assert i2 == tm.BLANK
                new_state = cls.RIGHT
        elif state == cls.RIGHT:
            if i1 != tm.BLANK:
                m1 = tm.RIGHT
            else:
                assert i1 == tm.BLANK
                assert i2 == tm.BLANK
                m1 = tm.LEFT
                m2 = tm.LEFT
                new_state = cls.ADD
                # We're at the right of both numbers. Add them, moving left
        elif state == cls.ADD:
            m1 = m2 = m3 = tm.LEFT
            if i1 == i2 == '0':
                o3 = '0'
            elif (i1 == '1' and i2 == '0') or (i1 == '0' and i2 == '1'):
                o3 = '1'
            elif i1 == '1' and i2 == '1':
                o3 = '0'
                new_state = cls.ADDCARRY
            elif i1 in (tm.BLANK, tm.START_A) and i2 in (tm.BLANK, tm.START_A):
                new_state = tm.HALT
            elif i1 in (tm.BLANK, tm.START_A):
                m1 = tm.STAY
                o3 = i2
            elif i2 in (tm.BLANK, tm.START_A):
                m2 = tm.STAY
                o3 = i1
            else:
                assert False, "What happened? %s %s" % (i1, i2)
        elif state == cls.ADDCARRY:
            m1 = m2 = m3 = tm.LEFT
            if i1 == i2 == '0':
                o3 = '1'
                new_state = cls.ADD
            elif (i1 == '1' and i2 == '0') or (i1 == '0' and i2 == '1'):
                o3 = '0'
            elif i1 == '1' and i2 == '1':
                o3 = '1'
            elif i1 in (tm.BLANK, tm.START_A) and i2 in (tm.BLANK, tm.START_A):
                o3 = '1'
                new_state = tm.HALT
            elif i1 in (tm.BLANK, tm.START_A):
                m1 = tm.STAY
                if i2 == '1':
                    o3 = '0'
                else:
                    assert i2 == '0'
                    o3 = '1'
                    new_state = cls.ADD
            elif i2 in (tm.BLANK, tm.START_A):
                m2 = tm.STAY
                if i1 == '1':
                    o3 = '0'
                else:
                    assert i1 == '0', "How is i1 %s?" % i1
                    o3 = '1'
                    new_state = cls.ADD
            else:
                assert False, "What happened?"
        else:
            raise ValueError("Unknown state %s" % state)
        return new_state, (o1, o2, o3), (m1, m2, m3)

    @classmethod
    def make(cls):
        pass
        """
        Returns a TM for PAL as in Example 1.1
        """
        # Make TM
        extra_states = [cls.COPY, cls.RIGHT, cls.ADD, cls.ADDCARRY]
        return tm.TuringMachine(
            None, # Use default alphabet,
            extra_states,
            cls.transition,
            3) # Input, work, output

class MULTIPLY(object):
    # Input, work, output
    # General plan:
    # 1. Copy 1st string to work tape, erasing it
    # 2. While 1st tape is nonzero:
    # 2.   Add tape 2 to output
    # 3.   Subtract 1 from tape 1
    pass


class TMEncoder(object):
    """
    Encodes a turing machine `m` as a string of 1s and 0s.
    
    We need to encode the following types of data:
        - number of tapes
        - alphabet
            - symbol name
            - separator
        - list of states
            - state name
            - separator
        - transition table
            - list of: current state, input list (with separators), output state, output writes, output moves
            - separators
        - separations between the above

    Our general strategy is to use "1" as the separator symbol, and encode all child data by
    replacing "1" with "01". So the separator is only valid if not preceded by a 1.

    We use the following enumeration convention...
        # Default alphabet:
     0  START_A = Letter('start')
     1  BLANK = Letter('blank')

        # Default states:
     0  QSTART = State('start')
     1  HALT = State('halt')

        # Movements
     0  LEFT = Move('left')
     1  STAY = Move('stay')
     2  RIGHT = Move('right')

    ...with user-defined alphabets and states following in arbitrary order.

    Pretty much everything else is implicit in the transition table, but we separate it out because it's easier.
    """
    def encode(self, bstring):
        return bstring.replace('1', '01')

    def decode(self, bstring):
        return bstring.replace('01', '1')

    def encode_and_pack(self, list_of_bstrings):
        return '1'.join(map(self.encode, list_of_bstrings))

    def _encode_set(self, s, first_entries):
        """
        `s` is an iterable of items to map to binary strings
        `first_entries` is an ordered iterable of the items to come first
        """
        item_list = []
        for entry in first_entries:
            s.remove(entry)
            item_list.append(entry)
        item_list += list(s)
        bstrs = [self.number_to_binary(i) for i, _ in enumerate(item_list)]
        result_map = dict(zip(item_list, bstrs))
        bstr = self.encode_and_pack(bstrs)
        return result_map, bstr
        
    def encode_alphabet(self, alphabet):
        """
        Returns (alpha_map, bstr) pair
        alpha_map: char -> num
        """
        return self._encode_set(alphabet, [tm.START_A, tm.BLANK])

    def encode_states(self, states):
        """
        Returns (state_map, bstr) pair
        state_map: state -> num
        """
        return self._encode_set(states, [tm.QSTART, tm.HALT])

    def encode_moves(self):
        return self._encode_set([tm.LEFT, tm.STAY, tm.RIGHT], [tm.LEFT, tm.STAY, tm.RIGHT])

    def encode_transitions(self, machine, num_tapes, alpha_map, state_map):
        """
        Binary string representing the machine's entire transition table.
        """
        result_bstrs = []
        move_map, _ = self.encode_moves()
        for state, state_bstr in state_map.items():
            if state == tm.HALT:
                # Transition is not defined from HALT state
                continue
            for input_alphas in itertools.product(*[alpha_map.keys()]*num_tapes):
                new_state, writes, moves = machine.transition_function(state, input_alphas)
                bstrs = []
                bstrs.append(state_map[state])
                bstrs.append(self.encode_and_pack([alpha_map[a] for a in input_alphas]))
                bstrs.append(state_map[new_state])
                bstrs.append(self.encode_and_pack([alpha_map[a] for a in writes]))
                bstrs.append(self.encode_and_pack([move_map[m] for m in moves]))
                bstr = self.encode_and_pack(bstrs)
                result_bstrs.append(bstr)
        return self.encode_and_pack(result_bstrs)

    def number_to_binary(self, n):
        assert n >= 0
        result = ['0']
        while n:
            if n % 2:
                assert result[-1] == '0'
                result[-1] = '1'
                n -= 1
            else:
                result.append('0')
                n /= 2
        return ''.join(reversed(result))

    def TM_to_binary(self, m):
        num_tapes, bstr_tapes = m._num_tapes, self.number_to_binary(m._num_tapes)
        alpha_map, bstr_alpha = self.encode_alphabet(m.alphabet)
        state_map, bstr_states = self.encode_states(m.states)
        bstr_tt = self.encode_transitions(m, num_tapes, alpha_map, state_map)

        result = [
            bstr_tapes,
            bstr_alpha,
            bstr_states,
            bstr_tt,
        ]
        return self.encode_and_pack(result)

    def __init__(self):
        return

def binary_to_TM(s):
    """Accepts a string of 1s and 0s and returns the TM it encodes."""

def test_encoding():
    e = TMEncoder()
    m = PAL.make()
    print e.TM_to_binary(m)

def test_PAL():
    input = sys.argv[1] if len(sys.argv) > 1 else '10101'
    input = list(input)
    m = PAL.make()
    m.run_on(input)
    m.printall()

def test_ADD():
    input = list('1001') + [tm.BLANK] + list('111')
    m = ADDER.make()
    m.run_verbosely(input)

if __name__ == '__main__':
    test_encoding()

