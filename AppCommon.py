from enum import Enum, IntEnum


class VideoMode(Enum):
    Board = 1
    Original = 2
    Markers = 3
    Detections = 4
    def __eq__(self, other):    return self.value ==  other.value
    def __ne__(self, other):    return self.value !=  other.value


class BoardState(IntEnum):
    Empty = 0
    Blue = 1
    Red = -1
    def __eq__(self, other):    return self.value ==  other.value
    def __ne__(self, other):    return self.value !=  other.value

