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
UTW_NAMING = [TIME, GAP, FORCE, "L1", "L2"]  # L(VDT)1 & 2 not used
KUL_NAMING = [TIME, DISPLACEMENT, FORCE]  # [s] , [mm], [kN]
JKU_NAMING = [TIME, TEMP, GAP, DISPLACEMENT, FORCE]  # in s, °C, mm, mm, N
ECN_NAMING = [TIME, FORCE, DISPLACEMENT, GAP, TEMP]  # [s] , [N], [mm], [mm], [°C]
RISE_NAMING = [
    TIME,
    "Cycle Elapsed Time",
    "Total Cycles",
    "Elapsed Cycles",
    "Step",
    "Total Cycle Count(8800 (10.0.0.2 : 0) Waveform)",
    DISPLACEMENT,  # "Position(8800 (10.0.0.2 : 0):Position) (mm)",
    FORCE,
    None,
]
TUM_NAMING = [FORCE, GAP, DISPLACEMENT, TEMP]
UOB_NAMING = [
    TIME,
    "CycleElapsedTime_s_",
    "TotalCycles",
    "ElapsedCycles",
    "Step",
    "TotalCycleCount_8800_0_3_Waveform_",
    GAP,
    FORCE,
]
WMG_NAMING = [TIME, DISPLACEMENT, GAP, "F0", "P1", "P2", "P3", "P4", "P5", "F1","FD", FORCE]
IVW_NAMING = [TIME, GAP, FORCE]
