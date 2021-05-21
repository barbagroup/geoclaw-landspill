# Dependencies, installation, and tests

The only operating system officially supported is Linux. We are not maintaining
compatibility with other systems, though they may still work.

---------------
## Dependencies

Build time and runtime dependencies are described in `requirements-build.txt`
and `requirements.txt`, respectively. `gfortran >= 8.0` is the only build time
dependency not included in the file, and, correspondingly, `libgfortran5 >= 8.0`
is the only runtime dependency not included in the file.

Anaconda users do not need to worry about dependencies at all.

On the other hand, `pip` users have to install `gfortran` or/and `libgfortran5`
in advance using the package managers of their Linux distributions. For example,
in Arch Linux, use:
```
# pacman -S gcc-fortran
```
And in Ubuntu 20.04:
```
# apt install gfortran
```

Alternatively, though not recommended, one can use `conda` to get `gfortran` and
then continue using `pip` for other dependencies. The command to get `gfortran`
from Anaconda is
```
$ conda install -c conda-forge "gfortran_linux-64>=8.0"
```
`conda` renames the compiler executable to `x86_64-conda-linux-gnu-gfortran`.
However, this should not concern users because CMake should be able to find it
automatically.

After installing `gfortran` manually, `pip` users can continue on the
installation of *geoclaw-landspill* (the next section).

---------------
## Installation

### Option 1: use `conda` and install binary files from Anaconda

As described in README, the following command creates an environment called
`landspill`, and it has *geoclaw-landspill* installed:
```
$ conda create \
    -n landspill -c barbagroup -c conda-forge \
    python=3.8 geoclaw-landspill
```
Once activate the environment, the executable `geoclaw-landspill` should already
be available.

### Option 2: use `pip` to install from PyPI or from source

Note, when using the `pip` command, users can always add the `--user` flag to
install to users' local paths and avoid root privilege. However, if using the
`--user` flag, users should make sure `pip`'s local `bin` path is in `PATH`.

#### Option 2.1: install from PyPI

To install the package from PyPI. 
```
$ pip install geoclaw-landspill
```

We only distribute source tarballs on PyPI due to the requirement of a Fortran
compiler. Wheels or binary releases of this package are not available. `pip`
will download the source tarball, compile/build the package, and then install
it. `gfortran` has to be installed in advance as described in the previous
section.

#### Option 2.2: install with a source tarball from GitHub

Download a release tarball from the repository's
[release page](https://github.com/barbagroup/geoclaw-landspill/releases) on GitHub,
and install the package directly with pip and the tarball:
```
$ pip install <tarball name>.tar.gz
```

#### Option 2.3: install with the repository in developer mode

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
$ pip install --editable .
```

Under the developer mode, installation is just a link referencing the source
directory, so any changes in the source Python files take effect immediately (
but not the Fortran files because they have to be re-compiled).

--------
## Tests

To run tests without installation, users can use
[`tox`](https://tox.readthedocs.io/en/latest/) to do so:

```
$ tox
```

End-users can run tests against the installed package if they install
*geoclaw-landspill* through `pip` and using the source tarball or code
repository. Use `pytest`:
```
$ pytest -v tests
```

Currently, the number and the coverage of the tests are limited. It's still a
WIP.
