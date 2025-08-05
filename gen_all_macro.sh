#!/bin/bash
python3 -m doors.hip.hip6
python3 -m doors.hip.hip7
python3 -m doors.hip.hip8
python3 -m doors.hip.hip9
python3 -m gen 6x6hip contained_ROM
python3 -m gen 7x7hip contained_ROM
python3 -m gen 8x8hip contained_ROM
python3 -m gen 9x9hip contained_ROM
