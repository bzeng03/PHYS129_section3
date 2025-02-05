import random
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Import your TM runner and definitions from 'a.py'
from a import run_turing_machine, transitions, wildcard_read, initial_state, final_states

###############################################################################
# Helper: Generate a random binary string of specified length, starting with '1'
###############################################################################
def random_binary_string_starting_with_one(length):
    """
    Return a random binary string of the specified 'length',
    ensuring:
      - length >= 1
      - first bit is '1'
      - the rest are random '0' or '1'
    """
    if length < 1:
        raise ValueError("Binary string length must be >= 1 to start with '1'.")
    return '1' + ''.join(random.choice('01') for _ in range(length - 1))

###############################################################################
# Build the tape and run the TM, returning the number of steps
###############################################################################
def run_tm_on_random_input(a, b, blanks=5):
    """
    1) Generate a random binary num1 of length 'a', and num2 of length 'b'.
    2) Build a tape of the form: B^blanks + num1 + '#' + num2 + '$' + B^blanks
    3) Run the Turing Machine (logging disabled), return the steps taken.
    """
    num1 = random_binary_string_starting_with_one(a)
    num2 = random_binary_string_starting_with_one(b)

    tape_str = "B" * blanks + num1 + "#" + num2 + "$" + "B" * blanks
    tape_list = list(tape_str)

    steps = run_turing_machine(
        tape_list,
        transitions,
        wildcard_read,
        initial_state,
        final_states,
        output_file="unused.dat",
        log_steps=False
    )
    return steps

###############################################################################
# Compute the 2D matrix of average steps, for 2 <= a,b <= max_dim
###############################################################################
def compute_average_steps_2d(max_dim=30, samples=5, blanks=5):
    """
    Create a 2D array `avg_steps[a-2, b-2]` holding the average TM steps
    for binary inputs of length a and b (each >= 2) across 'samples' random trials.

    :param max_dim: upper bound for a and b (from 2..max_dim inclusive)
    :param samples: how many random inputs to generate per (a,b)
    :param blanks: how many blanks to put on each side of the tape
    :return: A 2D NumPy array of shape (max_dim-1, max_dim-1) containing average steps
    """
    shape = (max_dim - 1, max_dim - 1)  # since we index from a=2..max_dim
    avg_steps = np.zeros(shape, dtype=float)

    # We'll do a nested loop over a and b in [2..max_dim].
    # For progress bar, we have (max_dim-1)*(max_dim-1) total cells.
    total_cells = (max_dim - 1) * (max_dim - 1)
    pbar = tqdm(total=total_cells, desc="Building 2D average steps")

    for a_idx, a_val in enumerate(range(2, max_dim + 1)):
        for b_idx, b_val in enumerate(range(2, max_dim + 1)):
            # Accumulate steps for multiple samples
            total_steps = 0
            for _ in range(samples):
                steps = run_tm_on_random_input(a_val, b_val, blanks=blanks)
                total_steps += steps

            avg = total_steps / samples
            avg_steps[a_idx, b_idx] = avg
            pbar.update(1)

    pbar.close()
    return avg_steps

###############################################################################
# Plot a 2D heatmap from the 2D array
###############################################################################
def plot_heatmap(heatmap_data, max_dim=30):
    """
    Plots a 2D heatmap of shape (max_dim-1, max_dim-1).
    X-axis ~ b in [2..max_dim], Y-axis ~ a in [2..max_dim].
    """
    plt.figure(figsize=(8, 6))

    # imshow expects [0..shape_x, 0..shape_y], but let's pass 'origin=lower'
    # so that the [0,0] index is in the bottom-left corner.
    img = plt.imshow(heatmap_data, 
                     origin='lower', 
                     cmap='viridis', 
                     aspect='auto')

    # Add a colorbar
    cbar = plt.colorbar(img)
    cbar.set_label("Average Steps to Halting")

    # Set the x/y ticks to reflect actual a,b from 2..max_dim
    ticks = np.arange(max_dim - 1)  # 0..(max_dim-2)
    labels = np.arange(2, max_dim + 1)  # 2..max_dim
    plt.xticks(ticks=ticks, labels=labels)
    plt.yticks(ticks=ticks, labels=labels)

    plt.xlabel("Length of num2 (b)")
    plt.ylabel("Length of num1 (a)")
    plt.title(f"2D Heatmap of Average Steps (2 ≤ a,b ≤ {max_dim})")
    plt.tight_layout()
    plt.show()

    # Optionally save the figure
    plt.savefig("heatmap_<n>.png")


def main():
    # We want a grid of a,b in [2..30].
    max_dim = 30
    samples = 5
    blanks = 5

    # 1) Compute the 2D matrix of average steps
    data_2d = compute_average_steps_2d(max_dim=max_dim, samples=samples, blanks=blanks)

    # 2) Plot as a heatmap
    plot_heatmap(data_2d, max_dim=max_dim)


if __name__ == "__main__":
    main()