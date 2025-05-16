"""Plot squeeze experiments of an institution."""

import pathlib as pl

import matplotlib.pyplot as plt

from smc_benchmark._naming import FORCE, GAP
from smc_benchmark.manipulate import crop_to_range, mean_std, print_data_structure
from smc_benchmark.read import read

# Name of the institution
institution = "kit"

# Folder with experimental data
folder = pl.Path("Path/to/data")

# Read experimental data
# - all data
data = read(institution, folder)
# - specific material and/or specification
# data = read(
#     institution, folder, mat_of_interest="CF5050K", spec_of_interest="7mm 100x100"
# )

# Log the loaded data to the console
print_data_structure(data)

# Define x and y axis names
x_name = GAP
y_name = FORCE

# Define the range of the x-axis
max_gap = 11.0  # [mm]
min_gap_map = {"7mm": 7.0, "5mm": 5.0, "3mm": 3.0}
min_gap_wildcard = 3.0  # [mm]

# What to plot? (Both can be set to True at the same time))
plot_samples = False  # plot individual experiments
plot_mean_std = True  # plot mean and std of the specification

# Plot
for material, configs in data.items():
    for config, experiments in configs.items():
        min_gap = next((v for k, v in min_gap_map.items() if k in config), min_gap_wildcard)
        experiments_cropped = crop_to_range(experiments, min_gap, max_gap, x_name, True)
        # Initialize figure
        fig, ax = plt.subplots(1, 1)

        # Set figure size
        fig.set_size_inches(3.5, 3.5)

        # Plot mean and std
        if plot_mean_std:
            x_interp, y_mean, y_std = mean_std(experiments_cropped, x_name, y_name)
            ax.fill_between(
                x_interp,
                y_mean - y_std,
                y_mean + y_std,
                color="black",
                alpha=0.1,
                label="Std",
            )
            ax.plot(
                x_interp,
                y_mean,
                color="black",
                label="Mean",
            )

        # Plot cropped data
        if plot_samples:
            for experiment in experiments_cropped:
                ax.plot(experiment[x_name], experiment[y_name], linestyle="--", alpha=0.5)

        ax.set_xlabel("Gap in mm")
        ax.set_ylabel("Force in N")

        # Custom handle if both samples and mean/std are plotted
        if plot_samples and plot_mean_std:
            handles, labels = ax.get_legend_handles_labels()
            # Add single handle for samples
            handle_samples = plt.Line2D([0], [0], linestyle="--", color="black", label="Samples")
            handles.append(handle_samples)
            labels.append("Samples")
            ax.legend(handles, labels)
        elif plot_mean_std:
            ax.legend()

        ax.set_title(f"{material} {config}")

        plt.grid(linestyle=":", alpha=0.5, color="silver")

        plt.tight_layout()

        plt.savefig(f"{material}_{config}.png", dpi=900)
        plt.close()
