#!/usr/bin/env bash
set -e
python -m doors.hip.hip10new
python -m gen 10x10hipnew ./tmp.schem
mv ./tmp.schem ~/Syncs/server-schematics/newgenhips/10x10/next2.schem
