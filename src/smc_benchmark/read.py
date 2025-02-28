import pathlib as pl

import numpy as np
import pandas as pd

from smc_benchmark._naming import KIT_NAMING, UT_NAMING
from smc_benchmark._utils import decode_filename

# Test configuirations
CONFIG1 = "3mm 100x100"
CONFIG2 = "3mm 50x50"
CONFIG3 = "5mm 100x100"
CONFIG4 = "7mm 100x100"

# Name of institution
KIT = "kit"
UT = "ut"

# Mapping between configuration and number for KIT, UT
CONFIG_TO_NUMBER_KIT = {
    CONFIG1: [3, 7, 11, 15, 19, 23],
    CONFIG2: [4, 8, 12, 16, 20, 24],
    CONFIG3: [2, 6, 10, 14, 18, 22],
    CONFIG4: [1, 5, 9, 13, 17, 21],
}
NUMBER_TO_CONFIG_KIT = {v: k for k, values in CONFIG_TO_NUMBER_KIT.items() for v in values}

# File extensions of the data files
FILE_EXTENSION = {KIT: "*.TXT", UT: "*.csv"}


def read(institution, folder):
    """Read test data.

    Parameters
    ----------
    institution : str
        Abbrevation of institution where the data was collected, e.g., 'kit' or 'ut'.
    folder : str | pathlib.Path
        Path to the folder containing the data.

    Returns
    -------
    dict[str, dict[str, list[pd.DataFrame]]]
        Dictionary containing the experimental data.
    """
    folder = pl.Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    # Read data
    all_data = {}
    for file in folder.glob(FILE_EXTENSION[institution]):
        _, material, number = decode_filename(file.stem)

        # Read individual experiments
        if institution == KIT:
            pd_data = _read_kit(file)
        elif institution == UT:
            pd_data = _read_ut(file)
        else:
            raise ValueError(f"Insitution '{institution}' not found")

        # Add experiment to all data
        if material not in all_data:
            all_data[material] = {}
        specification = NUMBER_TO_CONFIG_KIT[int(number)]
        if specification not in all_data[material]:
            all_data[material][specification] = []
        all_data[material][specification].append(pd_data)

    # TODO : Manipulate data to match the desired format
    return all_data


def _read_kit(file):
    """Read KIT data file."""
    data = np.loadtxt(file, delimiter=",", encoding="latin1", skiprows=5).T
    return pd.DataFrame(data[list(KIT_NAMING.keys())].T, columns=list(KIT_NAMING.values()))


def _read_ut(file):
    """Read UT/TPRC data file."""
    return pd.read_csv(file, sep=",", names=UT_NAMING, skiprows=6, quotechar='"')


def _read_tum():
    pass
