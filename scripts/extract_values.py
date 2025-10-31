"""Export unique values from experiments for statistical analysis."""

import pathlib as pl
from typing import Callable

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from smc_benchmark._naming import FORCE, GAP
from smc_benchmark.read import read

# ----------------------------------------------------------------------------
# Define paths and parameters
# ----------------------------------------------------------------------------
# Folder containing experimental data
results_folder_path = pl.Path(r"path\to\smc_benchmark_results")

# Folder to save extracted values
export_folder_path = results_folder_path.parent / "extracted_values"
export_folder_path.mkdir(parents=True, exist_ok=True)

# Gaps and secant widths to extract
GAPS = np.array([4.0, 7.0])
SECANT_WIDTH = 0.5  # width of range around the gap value for tangent slope


# Filtering function
def movingaverage(data: np.ndarray, width: int = 50) -> np.ndarray:
    """Moving average filter."""
    cumsum_vec = np.cumsum(np.insert(data, 0, 0))
    return (cumsum_vec[width:] - cumsum_vec[:-width]) / width


# Set filter_func to None to disable filtering
filter_func = None
# filter_func = movingaverage
# kwargs_filter = {"width": 30}

# ----------------------------------------------------------------------------
# Definition materials and specifications of interest
# ----------------------------------------------------------------------------
MATS_OF_INTEREST = [
    "CF6012K",
    "CF4012K",
    "CF6012K",
    "CF5012K",
    "CF503K",
    "CF5050K",
]

SPECS_OF_INTEREST = [
    "3mm 100x100",
    "3mm 50x50",
]

COMBS_TO_SKIP = [
    ("CF6012K", "3mm 50x50", "ivw"),  # load cell too large
    ("CF4012K", "3mm 50x50", "ivw"),  # load cell too large
    ("CF6012K", "3mm 50x50", "ivw"),  # load cell too large
    ("CF5012K", "3mm 50x50", "ivw"),  # load cell too large
    ("CF503K", "3mm 50x50", "ivw"),  # load cell too large
    ("CF5050K", "3mm 50x50", "ivw"),  # load cell too large
]

INSTITUTES_TO_SKIP = [
    # "ecn",
]

# ----------------------------------------------------------------------------
# Processing function
# ----------------------------------------------------------------------------


def process_exp(
    df: pd.DataFrame,
    gaps: np.ndarray,
    secant_width: np.ndarray,
    filter_func: Callable | None = None,
    filter_dx: float = 0.025,
    **kwargs_filter,
) -> np.ndarray:
    """Extract force and secant slopes of force at specified gaps."""
    # Interpolate force data
    f_interp = interp1d(df[GAP].values, df[FORCE].values)

    # Some simple checks
    gap_min, gap_max = df[GAP].min(), df[GAP].max()
    if np.any(gap_min > gaps) or np.any(gap_max < gaps):
        # Return NaNs if gaps are out of range
        return np.full((len(gaps), 3), np.nan)

    if filter_func is not None:
        # Make sure to apply filter independent of sampling rate
        start = np.ceil(gap_min / filter_dx)
        end = np.floor(gap_max / filter_dx)
        gap_equidistant = np.arange(start, end + 1) * filter_dx
        f_equidistant = f_interp(gap_equidistant)
        # Apply filter
        f_filtered = filter_func(f_equidistant, **kwargs_filter)
        gap_filtered = filter_func(gap_equidistant, **kwargs_filter)
        # Interpolate filtered data
        f_interp = interp1d(gap_filtered, f_filtered)
        f_hat = f_interp(gaps)
    else:
        # Force at specified gap values
        f_hat = f_interp(gaps)

    # Secante slope at specified gap values
    gap_lower = gaps - secant_width / 2
    gap_upper = gaps + secant_width / 2
    f_lower = f_interp(gap_lower)
    f_upper = f_interp(gap_upper)
    secant_slopes = (f_lower - f_upper) / secant_width

    return np.vstack((gaps, f_hat, secant_slopes)).T


# ----------------------------------------------------------------------------
# Loop through institutions
# ----------------------------------------------------------------------------
institution_folders = pl.Path(results_folder_path).glob("*/")
for institution_folder in institution_folders:
    institution = institution_folder.name.lower()
    if institution in INSTITUTES_TO_SKIP:
        continue
    print("## ------------------------------------------------------------ ##")
    print(f"# {institution}")
    print("## ------------------------------------------------------------ ##")

    # Let's simply read all data
    experiment_folder = institution_folder / f"{institution}_Press_Force_Data"
    data = read(
        institution,
        experiment_folder,
        skip_erroneous_files=True,
        verbose=False,
    )

    # Loop through individual experiments
    for mat_name, mat_data in data.items():
        for configuration, exp_data in mat_data.items():
            if configuration not in SPECS_OF_INTEREST:
                continue
            if not isinstance(exp_data, dict):
                print(f"Unexpected data structure for {mat_name} {configuration} at {institution}")
                continue
            for identifier, df in exp_data.items():
                if (mat_name, configuration, institution) in COMBS_TO_SKIP:
                    continue
                export_data = process_exp(df, GAPS, SECANT_WIDTH, filter_func=movingaverage)

                # CSV export
                # - file name
                output_folder = export_folder_path / institution.upper()
                output_folder.mkdir(parents=True, exist_ok=True)
                file_path = (
                    output_folder / f"{institution.upper()}-{mat_name.upper()}-"
                    f"{configuration.split(' ')[-1]}-{identifier}.csv"
                )
                # - rows: gap, force, secante
                np.savetxt(
                    file_path,
                    export_data,
                    delimiter=",",
                    header=f"Gap [mm],Force [N],Secant Slope (width {SECANT_WIDTH} mm) [N/mm]",
                    comments="",
                )
