from enum import Enum
from enum import unique


@unique
class OType(Enum):
    NONE = 0
    EGO = 1
    LANE = 2
    VEHICLE = 3
    SEGMENT = 4
    DISK = 5
    PEG = 6
