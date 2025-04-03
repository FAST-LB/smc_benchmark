import re

NAMING_PATTERN = r"(\w+)-(\w+)-(\d+)"


def decode_filename(filename):
    """Decode file name following predefined naming pattern."""
    # Unify naming
    filename = filename.replace("_", "-")

    match = re.match(NAMING_PATTERN, filename)
    if match:
        organization, material, number = match.groups()
    else:
        raise Exception(f"File name does not match pattern: {filename}")
    return organization, material, number
