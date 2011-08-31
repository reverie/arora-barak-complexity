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
        if state == tm.START_S:
            o2 = tm.START_A
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
            if i1 != tm.START_S:
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
        num_tapes = 1
        return tm.TuringMachine(
            None, # Use default alphabet,
            extra_states,
            cls.transition,
            3) # Input, work, output


if __name__ == '__main__':
    input = sys.argv[1] if len(sys.argv) > 1 else '10101'
    input = list(input)
    m = PAL.make()
    m.run(input)
    # TODO: print output

