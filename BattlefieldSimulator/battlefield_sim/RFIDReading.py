
from enum import Enum

# Have different levels, where if one specific one is detected, overwrite the others.
# Ie: Let the have team flag markers, that if the normal detection isn't picking it up, the tag marker can be put in a place that is more
# easily detected, and if the tag marker is detected, it overwrites the normal detection.


class ObjectiveControlLevel(Enum):
    NONE =   1
    SMALL =  2
    LARGE =  3
    FLAG =   4 #Flag overwrites all Non flag levels, and is used for team flag markers. If the flag is detected, it overwrites the other levels

def determine_control_level(detection_data):
    
    for data in detection_data:
        if data['type'] == 'flag':
            return ObjectiveControlLevel.FLAG
        elif data['type'] == 'large':
            return ObjectiveControlLevel.LARGE
        elif data['type'] == 'small':
            return ObjectiveControlLevel.SMALL
