"""Read test data from different institutions."""

import pathlib as pl

import numpy as np
import pandas as pd

from smc_benchmark._naming import (
    DISPLACEMENT,
    ECN_NAMING,
    FORCE,
    GAP,
    IVW_NAMING,
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
IVW = "ivw"

# Mapping between configuration and number for KIT, UT, KUL, IVW
CONFIG_TO_NUMBER_KIT = {
    CONFIG1: [3, 7, 11, 15, 19, 23],
    CONFIG2: [4, 8, 12, 16, 20, 24],
    CONFIG3: [2, 6, 10, 14, 18, 22],
    CONFIG4: [1, 5, 9, 13, 17, 21],
}

CONFIG_TO_NUMBER_JKU = {
    CONFIG1: [4, 8, 12, 16, 20, 24],
    CONFIG2: [3, 7, 11, 15, 19, 23],
    CONFIG5: [2, 6, 10, 14, 18, 22],
    CONFIG6: [1, 5, 9, 13, 17, 21],
}

# all short shots, 50x50 only
CONFIG_TO_NUMBER_UOB = {
    CONFIG6: [1, 5, 9, 13, 17, 21],  # 7 short shot
    CONFIG5: [2, 6, 10, 14, 18, 22],  # 5 short shot
    CONFIG2: [3, 7, 11, 15, 19, 23],  # 3 short shot
}

CONFIG_TO_NUMBER_RISE = {
    # CONFIG1: [4, 8, 12, 16, 20, 24],  # circular samples, not considered here
    CONFIG2: [3, 7, 11, 15, 19, 23],
    CONFIG5: [2, 6, 10, 14, 18, 22],
    CONFIG6: [1, 5, 9, 13, 17, 21],
}

CONFIG_TO_NUMBER_TUM = {
    CONFIG1: [3, 7, 11, 15, 19, 20, 23],  # Additional sample here
    CONFIG2: [4, 8, 12, 16, 24],  # One sample lacking
    CONFIG3: [2, 6, 10, 14, 18, 22],
    CONFIG4: [1, 5, 9, 13, 17, 21],
}

NUMBER_TO_CONFIG_KIT = {v: k for k, values in CONFIG_TO_NUMBER_KIT.items() for v in values}
NUMBER_TO_CONFIG_JKU = {v: k for k, values in CONFIG_TO_NUMBER_JKU.items() for v in values}
NUMBER_TO_CONFIG_UOB = {v: k for k, values in CONFIG_TO_NUMBER_UOB.items() for v in values}
NUMBER_TO_CONFIG_RISE = {v: k for k, values in CONFIG_TO_NUMBER_RISE.items() for v in values}
NUMBER_TO_CONFIG_TUM = {v: k for k, values in CONFIG_TO_NUMBER_TUM.items() for v in values}

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
    IVW: "*.csv",
}


def read(
    institution,
    folder,
    mat_of_interest=None,
    spec_of_interest=None,
    skip_erroneous_files=True,
    verbose=True,
):
    """Read test data.

    Parameters
    ----------
    institution : str
        Abbrevation of institution where the data was collected, e.g., 'kit' or 'utw'.
    folder : str | pathlib.Path
        Path to the folder containing the data.
    mat_of_interest : str | None
        Material of interest, e.g., 'CF5050K'. If None, all materials are read.
    spec_of_interest : str | None
        Specification of interest, e.g., '3mm 100x100'. If None, all specifications are read.
    skip_erroneous_files : bool
        If True, skip files listed in error.log located in the folder.
        Error log format: one erroneous filename per line, followed by a colon and the error
        message. An exemplary error log ::

            sample1.csv: Error message
            sample2.csv: Another error message

    verbose : bool
        If True, print information about the reading process.

    Returns
    -------
    dict[str, dict[str, dict[int, pd.DataFrame]]]
        Dictionary containing the experimental data.
    """
    folder = pl.Path(folder)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    # Check for errorneous files
    error_log_file = folder / "error.log"
    if skip_erroneous_files and error_log_file.exists():
        erroneous_files = _read_error_log(error_log_file)
    else:
        erroneous_files = []

    # Read data
    all_data = {}
    files = list(folder.glob(FILE_EXTENSION[institution]))  # Generator in Liste umwandeln
    if verbose:
        print(f"📁 Total number of {institution} data files: {len(files)}")
    n_files_read = 0
    for file in folder.glob(FILE_EXTENSION[institution]):
        if file.name.lower() in erroneous_files:
            if verbose:
                print(f"Skipping erroneous file: {file.name}")
            continue
        _, material, number = decode_filename(file.stem)

        # Determine the specification based on the institution
        try:
            if institution == JKU:
                specification = NUMBER_TO_CONFIG_JKU[int(number)]
            elif institution == UOB:
                specification = NUMBER_TO_CONFIG_UOB[int(number)]
            elif institution == RISE:
                specification = NUMBER_TO_CONFIG_RISE[int(number)]
            elif institution == TUM:
                specification = NUMBER_TO_CONFIG_TUM[int(number)]
            else:
                specification = NUMBER_TO_CONFIG_KIT[int(number)]
        except KeyError:
            print(f"Material {material} file number {int(number)} is not in CONFIG_TO_NUMBER_")
            continue

        # Skip materials that are not of interest
        if mat_of_interest:
            if material != mat_of_interest:
                continue
        if spec_of_interest:
            if spec_of_interest != specification:
                continue

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
        elif institution == IVW:
            pd_data = _read_ivw(file)
        else:
            raise ValueError(f"Insitution '{institution}' not found")

        # Add experiment to all data
        if material not in all_data:
            all_data[material] = {}

        # Add specification to all data
        if specification not in all_data[material]:
            all_data[material][specification] = {}
        all_data[material][specification][int(number)] = pd_data
        n_files_read += 1
    if verbose:
        print(f"... loaded {n_files_read} {institution} data files.")
    return all_data


def _read_kit(file):
    """Read KIT data file."""
    data = np.loadtxt(file, delimiter=",", encoding="latin1", skiprows=5).T
    return pd.DataFrame(data[list(KIT_NAMING.keys())].T, columns=list(KIT_NAMING.values()))


def _read_utw(file):
    """Read UT/TPRC data file."""
    data = pd.read_csv(file, sep=",", names=UTW_NAMING, skiprows=7, quotechar='"')
    data[GAP] = -data[GAP]
    data[DISPLACEMENT] = data[GAP][0] - data[GAP]
    return data


def _read_kul(file):
    """Read KUL data file."""
    data = pd.read_csv(file, sep=";", names=KUL_NAMING, skiprows=5, quotechar='"', decimal=",")
    data[FORCE] *= 1_000  # Convert kN to N
    data[GAP] = 11.0 - data[DISPLACEMENT]
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
    data[GAP] = data[GAP] - 0.05  # adjust gap
    data = data[data[GAP] <= 11.0].reset_index(drop=True)  # only consider gap <= 11 mm
    data[DISPLACEMENT] -= data[DISPLACEMENT][0]  # adjust displacement
    return data


def _read_uob(file):
    """Read UOB data file."""
    data = pd.read_csv(file, sep=",", names=UOB_NAMING, skiprows=1, encoding="latin1", decimal=".")
    data[FORCE] *= -1_000
    data[GAP] += 11.0
    data = data[data[GAP] <= 11.0].reset_index(drop=True)  # only consider gap <= 11 mm
    data[DISPLACEMENT] = data[GAP][0] - data[GAP]
    return data


def _read_wmg(file):
    """Read WMG data file."""
    data = pd.read_csv(file, sep=",", names=WMG_NAMING, skiprows=1, encoding="latin1", decimal=".")
    data[FORCE] *= 1_000.0  # [kN] to [N]
    data[DISPLACEMENT] = data[GAP][0] - data[GAP]
    return data


def _read_ecn(file):
    """Read ECN data file."""
    data = pd.read_csv(file, sep=";", names=ECN_NAMING, skiprows=3, encoding="latin1", decimal=".")
    data = data.loc[data[GAP] <= 11].reset_index(drop=True)
    data[DISPLACEMENT] = data[GAP][0] - data[GAP]
    return data


def _read_rise(file):
    """Read RISE data file."""
    data = pd.read_csv(file, sep=";", names=RISE_NAMING, skiprows=2, encoding="latin1", decimal=",")
    data[FORCE] *= -1_000.0  # [kN] to [N]
    data[GAP] = 41.10 + (data[DISPLACEMENT] - data[DISPLACEMENT].iloc[0])
    data = data[data[GAP] <= 11].reset_index(drop=True)
    data[DISPLACEMENT] = data[GAP][0] - data[GAP]
    return data


def _read_ivw(file):
    """Read IVW data file."""
    data = pd.read_csv(
        file, sep=";", names=IVW_NAMING, skiprows=4, quotechar='"', skipfooter=1, engine="python"
    )
    data[FORCE] *= 1_000  # Convert kN to N
    return data


def _read_error_log(file):
    """Read error log and return a list of erroneous files (lowercase)."""
    erroneous_files = []

    try:
        with file.open("r") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Warning: Could not read error log {file.as_posix()}: {e}")
        return erroneous_files

    for line_num, line in enumerate(lines, start=1):
        # Check formatting
        if ":" not in line:
            print(
                f"Warning: Malformed line {line_num} in error log {file.as_posix()}: "
                f"'{line.strip()}'"
            )
            continue

        # Extract filename
        try:
            filename = line.split(":")[0].strip()
            if filename:
                erroneous_files.append(filename.lower())
            else:
                print(
                    f"Warning: Line {line_num} in error log {file.as_posix()} has empty filename: "
                    f"{line}"
                )
        except Exception as e:
            print(
                f"Warning: Could not parse line {line_num} in error log {file.as_posix()}: "
                f"{line} - {e}"
            )
            continue
    return erroneous_files
