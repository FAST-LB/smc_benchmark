"""Script to evaluate the density and areal weight."""

import pathlib as pl

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

###############################################################################
# Define path to Excel file
###############################################################################
excel_file_path = pl.Path(r"path/to/file")

###############################################################################
# Load data from Excel sheets
###############################################################################
materials_to_plot = ["CF5050K", "CF5012K", "CF503K", "CF6012K", "CF4012K"]
material_data = {mat: [] for mat in materials_to_plot}

# Load data from Excel sheets
sheets = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"]
data_dict = {}

# Loop through each sheet
for sheet in sheets:
    df = pd.read_excel(excel_file_path, sheet_name=sheet, skiprows=18)  # Start from row 20
    df = df.dropna(subset=[df.columns[1]], how="all")  # Stop when empty row

    for _index, row in df.iterrows():
        material = row.iloc[1]
        weight = float(row.iloc[10]) if not pd.isna(row.iloc[10]) else np.nan
        Thickness = float(row.iloc[11]) / 1000 if not pd.isna(row.iloc[11]) else np.nan
        side_lengths = float(row.iloc[4]) / 1000 if not pd.isna(row.iloc[4]) else np.nan

        if not pd.isna(side_lengths) and isinstance(side_lengths, (int, float)):
            area = side_lengths**2
        else:
            area = np.nan

        density = row.iloc[12] if not pd.isna(row.iloc[12]) else np.nan

        if not pd.isna(weight) and not pd.isna(area) and area > 0:
            surface_weight = weight / area / 6
        else:
            surface_weight = np.nan

        # Split material name at the hyphen and take the first part
        material_name = material.split("-")[0]

        # Check if the material name is in the materials_to_plot list
        if material_name in materials_to_plot:
            material_data[material_name].append(
                {
                    "Specimen Weight": weight,
                    "Specimen Thickness": Thickness,
                    "Area": area,
                    "Density": density,
                    "Surface Weight": surface_weight,
                }
            )
# Convert to DataFrame
for material, data in material_data.items():
    material_data[material] = pd.DataFrame(data)

###################################################################
# Plot
##########################################################################
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(9, 4))
print(material_data.keys())
for material, data in material_data.items():
    ax1.errorbar(
        material,
        data["Specimen Thickness"].mean() * 1000,  # m to mm
        yerr=data["Specimen Thickness"].std() * 1000,  # m to mm
        fmt="o",
        label="Mean thickness",
        capsize=5,
    )
    ax2.errorbar(
        material,
        data["Density"].mean(),
        yerr=data["Density"].std(),
        fmt="o",
        label="Mean Density",
        capsize=5,
    )
    ax3.errorbar(
        material,
        data["Surface Weight"].mean(),
        yerr=data["Surface Weight"].std(),
        fmt="o",
        label="Mean Surface Weight",
        capsize=5,
    )

ax1.set_ylabel("Thickness in mm")
ax2.set_ylabel("Density in $kg/m^3$")
ax3.set_ylabel("Areal Weight in $g/m^2$")

angle = 45
ax1.set_xticks(range(len(material_data.keys())))
ax1.set_xticklabels(list(material_data.keys()), rotation=angle)
ax2.set_xticks(range(len(material_data.keys())))
ax2.set_xticklabels(list(material_data.keys()), rotation=angle)
ax3.set_xticks(range(len(material_data.keys())))
ax3.set_xticklabels(list(material_data.keys()), rotation=angle)

ax1.grid(alpha=0.5, linestyle=":")
ax2.grid(alpha=0.5, linestyle=":")
ax3.grid(alpha=0.5, linestyle=":")

plt.tight_layout()

# Save the plot
# file_path = excel_file_path.parent / "density_and_thickness.png"
# plt.savefig(file_path, dpi=300)

plt.show()
