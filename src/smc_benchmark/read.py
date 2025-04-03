"""Read test data from different institutions."""

import pathlib as pl

import numpy as np
import pandas as pd

from smc_benchmark._naming import (
    ECN_NAMING,
    FORCE,
    GAP,
    JKU_NAMING,
    KIT_NAMING,
    KUL_NAMING,
    RISE_NAMING,
    TUM_NAMING,
    UOB_NAMING,
    UTW_NAMING,
    WMG_NAMING,
)
from smc_benchmark._utils import decode_filename

# Test configuirations
CONFIG1 = "3mm 100x100"
CONFIG2 = "3mm 50x50"
CONFIG3 = "5mm 100x100"
CONFIG4 = "7mm 100x100"
CONFIG5 = "5mm 50x50"
CONFIG6 = "7mm 50x50"

# Name of institution
KIT = "kit"
UTW = "utw"
KUL = "kul"
ECN = "ecn"
RISE = "rise"
TUM = "tum"
UOB = "uob"
WMG = "wmg"
JKU = "jku"

# Mapping between configuration and number for KIT, UT, KUL
CONFIG_TO_NUMBER_KIT = {
    CONFIG1: [3, 7, 11, 15, 19, 23],
    CONFIG2: [4, 8, 12, 16, 20, 24],
    CONFIG3: [2, 6, 10, 14, 18, 22],
    CONFIG4: [1, 5, 9, 13, 17, 21],
}

CONFIG_TO_NUMBER_JKU = {
    CONFIG1: [1, 2, 3, 4, 5, 6],
    CONFIG2: [7, 8, 9, 10, 11, 12],
    CONFIG5: [25, 26, 27, 28, 29, 30],
    CONFIG6: [31, 32, 33, 34, 35, 36],
}

NUMBER_TO_CONFIG_KIT = {v: k for k, values in CONFIG_TO_NUMBER_KIT.items() for v in values}
NUMBER_TO_CONFIG_JKU = {v: k for k, values in CONFIG_TO_NUMBER_JKU.items() for v in values}

# File extensions of the data files
FILE_EXTENSION = {
    KIT: "*.TXT",
    UTW: "*.csv",
    KUL: "*.csv",
    ECN: "*.csv",
    RISE: "*.csv",
    TUM: "*.csv",
    UOB: "*.csv",
    WMG: "*.csv",
    JKU: "*.csv",
}


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
        elif institution == UTW:
            pd_data = _read_utw(file)
        elif institution == KUL:
            pd_data = _read_kul(file)
        elif institution == JKU:
            pd_data = _read_jku(file)
        elif institution == ECN:
            pd_data = _read_ecn(file)
        elif institution == RISE:
            pd_data = _read_rise(file)
        elif institution == TUM:
            pd_data = _read_tum(file)
        elif institution == UOB:
            pd_data = _read_uob(file)
        elif institution == WMG:
            pd_data = _read_wmg(file)
        else:
            raise ValueError(f"Insitution '{institution}' not found")

        # Add experiment to all data
        if material not in all_data:
            all_data[material] = {}
        # Determine the specification based on the institution
        if institution == JKU:
            specification = NUMBER_TO_CONFIG_JKU[int(number)]
        else:
            specification = NUMBER_TO_CONFIG_KIT[int(number)]
        if specification not in all_data[material]:
            all_data[material][specification] = []
        all_data[material][specification].append(pd_data)
    return all_data


def _read_kit(file):
    """Read KIT data file."""
    data = np.loadtxt(file, delimiter=",", encoding="latin1", skiprows=5).T
    return pd.DataFrame(data[list(KIT_NAMING.keys())].T, columns=list(KIT_NAMING.values()))


def _read_utw(file):
    """Read UT/TPRC data file."""
    return pd.read_csv(file, sep=",", names=UTW_NAMING, skiprows=6, quotechar='"')


def _read_kul(file):
    """Read KUL data file."""
    data = pd.read_csv(file, sep=";", names=KUL_NAMING, skiprows=5, quotechar='"', decimal=",")
    data[FORCE] *= 1_000  # Convert kN to N
    return data


def _read_jku(file):
    """Read JKU data file."""
    return pd.read_csv(
        file, sep="\t", names=JKU_NAMING, skiprows=5, quotechar='"', encoding="ISO-8859-1"
    )


def _read_tum(file):
    """Read TUM data file."""
    data = pd.read_csv(file, sep=";", names=TUM_NAMING, skiprows=1, encoding="latin1", decimal=",")
    data[GAP] *= -1
    return data


def _read_uob(file):
    """Read UOB data file."""
    data = pd.read_csv(file, sep=",", names=UOB_NAMING, skiprows=1, encoding="latin1", decimal=".")
    data[FORCE] *= -1_000
    data[GAP] *= -1
    return data


def _read_wmg(file):
    """Read WMG data file."""
    data = pd.read_csv(file, sep=",", names=WMG_NAMING, skiprows=1, encoding="latin1", decimal=".")
    data[FORCE] *= -1_000.0  # [kN] to [N]
    return data


def _read_ecn(file):
    """Read ECN data file."""
    data = pd.read_csv(file, sep=";", names=ECN_NAMING, skiprows=3, encoding="latin1", decimal=".")
    return data


def _read_rise(file):
    """Read RISE data file."""
    data = pd.read_csv(file, sep=";", names=RISE_NAMING, skiprows=2, encoding="latin1", decimal=",")
    data[FORCE] *= -1_000.0  # [kN] to [N]
    return data
