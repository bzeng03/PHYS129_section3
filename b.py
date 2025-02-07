def generate_and_save_tape(num1, num2, blanks, filename):
    """
    Generate a Turing machine tape of the form:
        B...B(num1)#(num2)$B...B
    with 'blanks' blank symbols on both the left and right sides.
    Then append the tape to the given filename (a .dat file).

    :param num1: Binary string for the first number (e.g., "1011").
    :param num2: Binary string for the second number (e.g., "100").
    :param blanks: The number of blank symbols 'B' for both left and right sides.
    :param filename: The .dat file to append the tape string to.
    :return: The generated tape as a string.
    """
    # Construct the tape
    tape = "B" * blanks + num1 + "#" + num2 + "$" + "B" * blanks

    # Append the tape to the given .dat file
    with open(filename, 'a') as f:
        f.write(tape + "\n")

    return tape


# Example usage:
if __name__ == "__main__":
    # This will generate a tape for num1=1011 and num2=100 with 6 blanks each side
    # and append it to "tapes.dat", then print the tape.
    result_tape = generate_and_save_tape("101001010111", "101000101", 6, "example_initial_tape.dat")
    result_tape = generate_and_save_tape("101111", "101001", 6, "example_initial_tape.dat")
    print("Generated tape:", result_tape)