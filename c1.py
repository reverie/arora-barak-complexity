import sys

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


if __name__ == '__main__':
    # Test PAL
    #input = sys.argv[1] if len(sys.argv) > 1 else '10101'
    #input = list(input)
    #m = PAL.make()
    #m.run_on(input)
    #m.printall()

    # Test ADD
    input = list('1001') + [tm.BLANK] + list('111')
    m = ADDER.make()
    m.run_verbosely(input)

