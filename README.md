# Creating PyPi wheels from conda-forge for chemfiles

This repository contains a script that can create wheels for chemfiles from the
conda-forge build. This script should be able to run from any platform (but was
only tested on OS X/Linux), and generate all wheels from this single platform.

```bash
pip install -r requirements.txt
./build-wheels.py
```

The wheels are in `build/dist`. To publish them to PyPi, one should use twine:

```
twine upload build/dist/*
```
