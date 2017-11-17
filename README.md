# Creating PyPi wheels from conda-forge for chemfiles

This repository contains a script that can create wheels for chemfiles from the
conda-forge build. This script should be able to run from any platform (but was
only tested on OS X), and generate all wheels from this single platform.


```bash
pip install -r requirements.txt
./build-wheels.py
```
