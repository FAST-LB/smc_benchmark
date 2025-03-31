"""Row to pandas naming."""

# Define variable names
GAP = "h"  # molding gap, or sample thickness
TIME = "t"  # time
TEMP = "T"  # temperature
FORCE = "F"  # force
DISPLACEMENT = "d"  # displacement
VELOCITY = "v"  # velocity

# Column names; used in read functions
KIT_NAMING = {0: TIME, 2: FORCE, 3: DISPLACEMENT, 4: GAP}
UTW_NAMING = [TIME, DISPLACEMENT, FORCE, "L1", "L2"]  # L(VDT)1 & 2 not used
KUL_NAMING = [TIME, DISPLACEMENT, FORCE]  # [s] , [mm], [kN]
