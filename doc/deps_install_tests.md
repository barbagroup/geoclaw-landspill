# Dependencies, installation, and tests

The only operating system supported is Linux. We are not maintaining
compatibility with other systems, though they may still work.

---------------
## Dependencies

`pip` can install all except one dependency. File `requirements.txt` describes
runtime dependencies, and file `requirements-build.txt` describes additional
dependencies if building the package locally. When installing
*geoclaw-landspill* through `pip`, `pip` takes care of dependencies
automatically.

The only dependency that may need manual installation is the Fortran compiler.
We have only tested `gfortran`. After installation, users can remove the
compiler itself (i.e., `gfortran`). However, `libgfortran` may be needed during
runtime if using dynamic linking. For `gfortran` (and also `libgfortran`), the
minimum version is 8.

Installation of `gfortran` depends on the operating systems and virtual
environments. For example, in Arch Linux:
```
# pacman -S gcc-fortran
```
Ubuntu 20.04:
```
# apt install gfortran
```

Alternatively, one can use `conda` to get `gfortran` if using Anaconda virtual
environment:
```
$ conda install -c conda-forge "gfortran_linux-64>=8.0"
```
`conda` renames the compiler executable to `x86_64-conda-linux-gnu-gfortran`.
However, this should not concern users because CMake should be able to find it
automatically.

---------------
## Installation

Note, for the `pip` command and `python setup.py install`, users can always add
the `--user` flag to install to users' local paths and avoid root privilege.

### 1. Install from PyPI

The easiest way to install *geoclaw-landspill* is through PyPI. 
```
$ pip install geoclaw-landspill
```

We only distribute source tarballs on PyPI due to the requirement of a Fortran
compiler. Wheels or binary releases of this package are not available.

### 2. Install with a source tarball from GitHub

Download a release tarball from the repository's
[release page](https://github.com/barbagroup/geoclaw-landspill/releases) on GitHub,
and install the package directly with pip and the tarball:
```
$ pip install <tarball name>.tar.gz
```

### 3. Install with the repository

Clone/pull the repository from GitHub:
```
$ git clone --recurse-submodules https://github.com/barbagroup/geoclaw-landspill.git
```

Go into the folder, and then install the Python dependencies with:
```
$ pip install -r requirements.txt -r requirements-build.txt
```
Then, install *geoclaw-landspill*:
```
$ python setup.py install
```

--------
## Tests

To run tests without installation, users can use
[`tox`](https://tox.readthedocs.io/en/latest/) to do so:

```
$ tox
```

End-users can run tests against the installed package if they install
*geoclaw-landspill* through method
[2](#2.-install-with-a-source-tarball-from-github) and method
[3](#3.-install-with-the-repository). Use `pytest`:
```
$ pytest -v tests
```

Currently, the number and the coverage of the tests are limited. It's still a
WIP.
