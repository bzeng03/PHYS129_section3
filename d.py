import random
import matplotlib.pyplot as plt
from tqdm import tqdm  # For progress bar

from a import run_turing_machine, transitions, wildcard_read, initial_state, final_states


def random_binary_string_starting_with_one(length):
    """
    Return a random binary string of the specified 'length', 
    ensuring:
      - length >= 1
      - first bit is '1'
      - the rest are random '0' or '1'
    """
    if length < 1:
        raise ValueError("Binary string length must be at least 1 to start with '1'.")
    return '1' + ''.join(random.choice('01') for _ in range(length - 1))


def analyze_average_steps_vs_length(L_values, samples=10, blanks=5):
    """
    For each total length L in L_values (where L >= 2):
      1) Generate 'samples' random pairs (num1, num2) with len(num1) + len(num2) = L
         and both len(num1), len(num2) >= 1, each starting with '1'.
      2) Build the tape: B^blanks + num1 + '#' + num2 + '$' + B^blanks
      3) Run the TM (with logging disabled).
      4) Compute the average steps taken before halting.

    Returns a list of (L, average_steps).
    """
    results = []

    # Use tqdm to show progress for the loop over L_values
    for L in tqdm(L_values, desc="Analyzing lengths"):
        # If L < 2, skip or raise an error, because we can't have both strings >= 1 in length
        if L < 2:
            continue  # or raise ValueError("L must be >= 2 to have two valid binary numbers.")

        total_steps = 0
        for _ in range(samples):
            # 1 <= len_num1 < L, so len_num2 = L - len_num1 >= 1
            len_num1 = random.randint(1, L - 1)
            len_num2 = L - len_num1

            # Generate each number starting with '1'
            num1 = random_binary_string_starting_with_one(len_num1)
            num2 = random_binary_string_starting_with_one(len_num2)

            # Construct the tape
            tape_str = "B" * blanks + num1 + "#" + num2 + "$" + "B" * blanks
            tape_list = list(tape_str)

            # Run TM with logging turned off
            steps = run_turing_machine(
                tape_list,
                transitions,
                wildcard_read,
                initial_state,
                final_states,
                output_file="unused.dat",  # Not used if log_steps=False
                log_steps=False
            )
            total_steps += steps

        average_steps = total_steps / samples
        results.append((L, average_steps))

    return results


def plot_average_steps_histogram(L_values, samples=10, blanks=5):
    """
    1. Calls analyze_average_steps_vs_length to get average step data.
    2. Plots a histogram (bar plot) of the average steps vs. total length (L).
    """
    data = analyze_average_steps_vs_length(L_values, samples=samples, blanks=blanks)
    # data is a list of (L, average_steps)
    L_vals = [item[0] for item in data]
    avg_steps = [item[1] for item in data]

    plt.figure(figsize=(8, 6))
    plt.bar(L_vals, avg_steps, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title(
        f"Average Steps vs. Total Input Length (L)\n(samples={samples} random valid inputs each)"
    )
    plt.xlabel("Total Input Length L = len(num1) + len(num2) (each >= 1)")
    plt.ylabel("Average Steps to Halting")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    # Save the figure if desired
    plt.savefig("n(L_a,b)_vs_L_a,b.png")


def main():
    # Example usage:
    #   Analyze L from 2 to 12
    #   For each L, generate 10 random input pairs, measure steps, average them.
    #   Each num1, num2 >= 1 in length and must start with '1'.
    L_min, L_max = 2, 1000
    L_values = range(L_min, L_max + 1)  
    samples = 10
    blanks = 100

    plot_average_steps_histogram(L_values, samples, blanks)


if __name__ == "__main__":
    main()