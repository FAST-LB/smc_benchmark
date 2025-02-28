"""Plot all squeeze experiments of an institution."""

import pathlib as pl

import matplotlib.pyplot as plt

from smc_benchmark.read import read

# Folder with experimental data
folder = pl.Path(r"path/to/folder")

# Name of the institution
institution = "kit"

# Read experimental data
data = read(institution, folder)

# Plot all configurations
for material, configs in data.items():
    for config, experiments in configs.items():
        fig, ax = plt.subplots(1, 1)
        for experiment in experiments:
            ax.plot(experiment["h"], experiment["F"])
        ax.set_xlabel("Gap in mm")
        ax.set_ylabel("Force in N")
        ax.set_title(f"{material} {config}")
        plt.savefig(f"{material}_{config}.png", dpi=300)
        plt.close()
