"""Functions to manipulate experimental data."""

import numpy as np
from scipy.interpolate import interp1d

from smc_benchmark._naming import FORCE, GAP


def crop_to_range(data, start, end, column=GAP, crop_force=False):
    """Crop data to a specific range.

    Parameters
    ----------
    data : list[pd.DataFrame]
        Data to crop to range.
    start : float
        Start of the range.
    end : float
        End of the range.
    column : str, optional
        Column to crop, by default 'h'.
    crop_force : bool, optional
        If True, the data is additionally cropped at the max. force ('F'), by default False.

    Returns
    -------
    list[pd.DataFrame]
        Cropped data.
    """
    cropped_data = [df[(df[column] >= start) & (df[column] <= end)] for df in data]
    if crop_force:
        idxs_max_force = [df[FORCE].idxmax() for df in cropped_data]
        cropped_data = [df.loc[:idx] for idx, df in zip(idxs_max_force, cropped_data)]
    return cropped_data


def mean_std(data, x_col=GAP, y_col=FORCE):
    """Calculate mean and std of the data.

    Parameters
    ----------
    data : list[pd.DataFrame]
        Data to calculate mean and std.
    x_col : str, optional
        Column to use for x-axis, by default 'h'.
    y_col : str, optional
        Column to use for y-axis, by default 'F'.

    Returns
    -------
    tuple
        Tuple of x-axis values, mean and std.
    """
    x_min, x_max = data[0][x_col].min(), data[0][x_col].max()
    for df in data:
        x_min = max(x_min, df[x_col].min())
        x_max = min(x_max, df[x_col].max())
    if x_col == GAP:
        dx = 0.05
        start = np.ceil(x_min / dx)
        end = np.floor(x_max / dx)
        x_interp = np.arange(start, end + 1) * dx
    else:
        x_interp = np.linspace(x_min, x_max, 250)

    y_interp = []
    for df in data:
        y_f = interp1d(df[x_col].values, df[y_col].values)
        y_i = y_f(x_interp)
        y_interp.append(y_i)
    y_interp = np.array(y_interp)

    y_mean = np.mean(y_interp, axis=0)
    y_std = np.std(y_interp, axis=0)

    return x_interp, y_mean, y_std


def print_data_structure(data):
    """Print the available data structure."""
    for experiment in data.keys():
        print(f"Material: {experiment}")
        for specification, samples in data[experiment].items():
            print(f"|-- Experiment: {specification} (samples: {len(samples)})")
