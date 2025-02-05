#!/usr/bin/env python3

def from_code(code):
    """
    Parse lines of the form:
        old_state   read_symbol   write_symbol   direction   new_state
    where read_symbol or write_symbol may be '*' for wildcard.
    Returns (transitions, wildcard_read, initial_state, final_states).

    'transitions' is a dict with:
      {
        (old_state, read_symbol) : (write_symbol, direction, new_state),
        ...
      }
    We also keep a separate dict for wildcard reads:
      {
        old_state -> (write_symbol, direction, new_state)
      }
    so that if we do not find an exact match for (old_state, symbol),
    we fallback to wildcard if it exists.

    If write_symbol == '*', we interpret that as "write the same symbol".
    If direction == '*', we interpret that as "do not move the head".
    """
    lines = []
    for raw_line in code.split('\n'):
        # Remove any text after semicolon (comment) and strip
        line = raw_line.split(';', 1)[0].strip()
        if line:
            lines.append(line)

    transitions = {}
    wildcard_read = {}
    final_states = set()

    for i, line in enumerate(lines):
        old_state, read_symbol, write_symbol, direction, new_state = line.split()

        # If new_state starts with "halt", treat it as a final (halting) state
        if new_state.startswith('halt'):
            final_states.add(new_state)

        # store transitions
        if read_symbol == '*':
            # This is a wildcard read
            wildcard_read[old_state] = (write_symbol, direction, new_state)
        else:
            transitions[(old_state, read_symbol)] = (write_symbol, direction, new_state)

    # The initial state is taken from the first rule's old_state
    initial_state = lines[0].split()[0]

    return transitions, wildcard_read, initial_state, final_states


# Transition rules (as a big multiline string):
tm_code = """
90 # B r 90
90 $ B l 91
90 * * r 90
91 B B l 92
91 * * l 91
92 B B l 2
92 * * l 92

; Set up tally
0 * * l 1
1 B B l 2
2 B 0 r 3
3 B B r 10

; Find end of num1
10 B B l 11
10 # # l 11
10 0 0 r 10
10 1 1 r 10

; If last digit of num1 is 0, multiply num2 by 2
11 0 # r 20
; If last digit of num1 is 1, add num2 to tally and then multiply num2 by 2
11 1 # r 30

; Multiply num2 by 2
20 B B r 20
20 # # r 20
20 * * r 21
21 B 0 l 25 ; Multiplication by 2 done, return to end of num1
21 * * r 21
25 B B l 26
25 * * l 25
26 B B r 80 ; Finished multiplying. Clean up
26 # # l 26
26 0 0 * 11
26 1 1 * 11

; Add num2 to tally
30 B B r 30
30 # # r 30
30 * * r 31
31 B B l 32
31 * * r 31
32 0 y l 40 ; Add a zero
32 1 x l 50 ; Add a one
32 y y l 32
32 x x l 32
32 B B r 70 ; Finished adding
                                
; Adding a 0 to tally
40 B B l 41
40 * * l 40
41 B B l 41
41 * * l 42
42 B B l 43
42 * * l 42
43 y y l 43
43 x x l 43
43 0 y r 44
43 1 x r 44
43 B y r 44
44 B B r 45
44 * * r 44
45 B B r 45
45 * * r 46
46 B B r 47
46 * * r 46
47 B B r 47
47 * * r 48
48 B B l 32
48 * * r 48
                                      
; Adding a 1 to tally
50 B B l 51
50 * * l 50
51 B B l 51
51 * * l 52
52 B B l 53
52 * * l 52
53 y y l 53
53 x x l 53
53 B x r 55
53 0 x r 55
53 1 y l 54
54 0 1 r 55
54 1 0 l 54
54 B 1 r 55
55 B B r 56
55 * * r 55
56 B B r 56
56 * * r 57
57 B B r 58
57 * * r 57
58 B B r 58
58 * * r 59
59 B B l 32
59 * * r 59

; Finished adding, clean up
70 x 1 r 70
70 y 0 r 70
70 B B l 71
71 B B l 72
71 * * l 71
72 B B l 72
72 * * l 73
73 B B l 74
73 * * l 73
74 y 0 l 74
74 x 1 l 74
74 * * r 75
75 B B r 76
75 * * r 75
76 B B r 20
76 * * r 76

; Finished multiplying, clean up
80 # B r 80
80 B B r 81
81 B B l 82
81 * B r 81
82 B B l 82
82 * * * halt
"""

# Parse the transition rules into structures
transitions, wildcard_read, initial_state, final_states = from_code(tm_code)

def run_turing_machine(tape, 
                       transitions, 
                       wildcard_read, 
                       initial_state, 
                       final_states,
                       output_file='multiplication.dat',
                       log_steps=True):
    """
    Runs the Turing Machine on the given tape (list of symbols).
    
    Parameters:
    -----------
    tape          : list
        A list of symbols (characters) representing the TM tape.
    transitions   : dict
        A dict mapping (state, read_symbol) -> (write_symbol, direction, next_state).
    wildcard_read : dict
        A dict mapping (state) -> (write_symbol, direction, next_state) for wildcard reads.
    initial_state : str
        The name of the initial state of the Turing machine.
    final_states  : set
        A set of halting (final) states.
    output_file   : str
        The file to which all step-by-step configurations are appended (if logging is enabled).
    log_steps     : bool
        If True, append each step's configuration to output_file.
        If False, do not write anything to file.
    
    Returns:
    --------
    int
        The total number of steps executed before halting (or no transition).
    """

    head = 0
    current_state = initial_state
    step = 0

    # If we are logging, open the file in append mode
    f = None
    if log_steps:
        f = open(output_file, 'a')

    def record_configuration():
        """Write the current configuration to file (if logging is on)."""
        if not log_steps:
            return
        tape_str = ''.join(tape)
        f.write(f"Step {step:04d}: State={current_state}, Head={head}, Tape={tape_str}\n")

    # Record the initial configuration
    record_configuration()

    while True:
        # Check for halting
        if current_state in final_states:
            step += 1
            record_configuration()  # final state config
            break

        # Expand tape if head is out of range
        if head < 0:
            tape.insert(0, 'B')
            head = 0
        elif head >= len(tape):
            tape.append('B')

        read_symbol = tape[head]

        # Find the transition
        if (current_state, read_symbol) in transitions:
            write_symbol, direction, new_state = transitions[(current_state, read_symbol)]
        elif current_state in wildcard_read:
            write_symbol, direction, new_state = wildcard_read[current_state]
        else:
            # No transition found -> halt
            step += 1
            if log_steps:
                f.write(f"No transition found in state={current_state}, symbol={read_symbol}. Halting.\n")
            record_configuration()
            break

        # If we need to write the same symbol, keep the read_symbol
        if write_symbol == '*':
            write_symbol = read_symbol

        # Write to tape
        tape[head] = write_symbol

        # Move head if direction is 'l' or 'r'
        if direction == 'l':
            head -= 1
        elif direction == 'r':
            head += 1
        # if direction == '*', do not move

        # Update state
        current_state = new_state

        step += 1
        record_configuration()

    # Close file if we opened it
    if f is not None:
        f.close()

    # Return the total steps
    return step

filename = "tm_mult.dat"

def main(initial_tape):
    # Convert string into a list of symbols
    tape_list = list(initial_tape)
    # Run the TM
    run_turing_machine(tape_list, transitions, wildcard_read, initial_state, final_states,
                       output_file=filename)

if __name__ == "__main__":
    # We open the file in append mode just once here.
    with open(filename, 'a') as f:
        # Write a title line for the first calculation
        f.write("----------Calculation 1: 101001010111 * 101000101----------\n")
    # Now run the TM on the first input
    main(initial_tape="BBBBBBBBBBBBBB101001010111#101000101$BBBBBBBBBBBBBBBBBBB")

    with open(filename, 'a') as f:
        # Write a title line for the second calculation
        f.write("----------Calculation 2: 101111 * 101001----------\n")
    # Run the TM on the second input
    main(initial_tape="BBBBBBBBBBBB101111#101001$BBBBBBBBBBBB")