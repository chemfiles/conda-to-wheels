#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import yaml
import tarfile
import pprint
import shutil
import subprocess

if sys.version_info >= (3, 0):
    import urllib.request as request
else:
    import urllib as request

# Version information
VERSION = "0.7.4"
CHFL_PY_BUILD = "-py27_0"
CHFL_LIB_BUILD = "-1"
CHFL_LIB_BUILD_WIN = "-vc14_1"
PRE_RELEASE = ".dev0"

# Where to get the files from
CHFL_PY_ROOT = "https://anaconda.org/conda-forge/chemfiles-python"
CHFL_PY = "chemfiles-python-{VERSION}{CHFL_PY_BUILD}.tar.bz2"
CHFL_PY = CHFL_PY.format(VERSION=VERSION, CHFL_PY_BUILD=CHFL_PY_BUILD)

CHFL_LIB_ROOT = "https://anaconda.org/conda-forge/chemfiles-lib"
CHFL_LIB = "chemfiles-lib-{VERSION}{CHFL_LIB_BUILD}.tar.bz2"

SETUP_PY_BEGINING = """
# -*- coding: utf-8 -*-
import os
from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class WheelBuild(bdist_wheel):
    # Workaround until https://github.com/pypa/wheel/issues/185 is resolved
    def get_tag(self):
        tag = bdist_wheel.get_tag(self)
        return ('py2.py3', ) + tag[1:]
\n\n
"""

SETUP_PY_END = """\n\n
setup(
    name='chemfiles',
    author='Guillaume Fraux',
    author_email='guillaume@fraux.fr',
    include_package_data=True,
    cmdclass={'bdist_wheel': WheelBuild},
    packages=['chemfiles'],
    **metadata
)
"""

LOCATION = """
import os

dirname = os.path.dirname(__file__)
CHEMFILES_LOCATION = os.path.join(dirname, "{location}")
"""

PLATFORMS = [
    # pairs of conda, pypi platform definitions
    ('osx-64', 'macosx-10.9-x86_64'),
    # FIXME: we are not actually building a manylinux wheel, because
    # conda-forge is based on Centos 6 and not Centos 5. But Centos5 is going
    # to die soon, and there are plans to create a manylinux2 Docker image
    # based on Centos 6.
    ('linux-64', 'manylinux1-x86_64'),
    ('win-32', 'win32'),
    ('win-64', 'win-amd64'),
]


def mkdir(path):
    '''a mkdir that does not error when the path exists'''
    try:
        os.mkdir(path)
    except OSError:
        pass


def download(url, path, output=""):
    path = os.path.join(output, path)
    if not os.path.exists(path):
        print("downloading " + url)
        request.urlretrieve(url, path)
    return path


def get_python_source():
    url = "{chfl_py_root}/{version}/download/osx-64/{chfl_py}".format(
        chfl_py_root=CHFL_PY_ROOT,
        version=VERSION,
        chfl_py=CHFL_PY
    )

    path = download(url, CHFL_PY)
    with tarfile.open(path) as tar:
        libpath = "lib/python2.7/site-packages/chemfiles/"
        for member in tar.getmembers():
            if not member.isreg():
                continue

            # Python source
            if member.name.startswith(libpath) and member.name.endswith(".py"):
                basename = os.path.basename(member.name)
                member.name = os.path.join("chemfiles", basename)
                tar.extract(member)
            # Metadata file
            elif member.name == "info/recipe/meta.yaml":
                member.name = "meta.yaml"
                tar.extract(member)

    return yaml.load(open("meta.yaml"))


def download_library(conda):
    if 'win' in conda:
        chfl_lib = CHFL_LIB.format(
            VERSION=VERSION, CHFL_LIB_BUILD=CHFL_LIB_BUILD_WIN
        )
        libpath = "Library/bin"
    else:
        chfl_lib = CHFL_LIB.format(
            VERSION=VERSION, CHFL_LIB_BUILD=CHFL_LIB_BUILD
        )
        libpath = "lib/lib"

    url = "{chfl_lib_root}/{version}/download/{conda}/{chfl_lib}".format(
        chfl_lib_root=CHFL_LIB_ROOT,
        version=VERSION,
        conda=conda,
        chfl_lib=chfl_lib
    )

    location = ""
    path = download(url, chfl_lib, conda)
    with tarfile.open(path) as tar:
        for member in tar.getmembers():
            if not member.isreg():
                continue

            if member.name.startswith(libpath):
                basename = os.path.basename(member.name)
                member.name = os.path.join("chemfiles", basename)
                location = basename
                tar.extract(member)

    return location


if __name__ == '__main__':
    mkdir("build")
    os.chdir(os.path.join("build"))
    metadata = get_python_source()

    requirements = [
        r for r in metadata['requirements']['run']
        if not (r.startswith("chemfiles") or r.startswith("python"))
    ]
    metadata = {
        'version': metadata['package']['version'] + PRE_RELEASE,
        'description': metadata['about']['summary'],
        'url': metadata['about']['home'],
        'license': metadata['about']['license'],
        'install_requires': requirements,
    }

    for platform in PLATFORMS:
        conda, pypi = platform
        mkdir(conda)

        lib_location = download_library(conda)
        metadata['package_data'] = {'chemfiles': [lib_location]}

        with open("setup.py", "w") as fd:
            fd.write(SETUP_PY_BEGINING)
            fd.write("metadata = " + pprint.pformat(metadata, width=1))
            fd.write(SETUP_PY_END)

        with open(os.path.join("chemfiles", "location.py"), "w") as fd:
            fd.write(LOCATION.format(location=lib_location))

        subprocess.call(
            [sys.executable, "setup.py", "bdist_wheel", "--plat-name=" + pypi]
        )

        os.remove(os.path.join("chemfiles", lib_location))
        shutil.rmtree("build")
