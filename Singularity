# vim:ft=singularity

# the base image is ubuntu 18.04 
Bootstrap: library
From: ubuntu:18.04

# environment variablae DURING RUNTIME
%environment
    export PYTHON=python3
    export FC=gfortran-8
    export MPLBACKEND=agg
    export CLAW=/opt/clawpack
    export PYTHONPATH=/opt/clawpack
    export LANDSPILL=/opt/geoclaw-landspill-cases

# =============================================================================
# commands after pulling the base ubuntu image
# =============================================================================
%post
    # save the date when this image is built
    NOW=`date`
    echo "export NOW=\"${NOW}\"" >> $SINGULARITY_ENVIRONMENT

    # setup container time zone info (needed in Dockerfile)
    ln -snf /usr/share/zoneinfo/UTC /etc/localtime
    echo "UTC" > /etc/timezone 

    # install required package from Ubuntu package repository
    apt-get update
    apt-get -y --no-install-recommends install \
        make \
        git \
        ca-certificates \
        gfortran-8 \
        python3 \
        python3-pip
    rm -rf /var/lib/apt/lists/*

    # change the default python to python 3
    ln -s /usr/bin/python3 /usr/bin/python

    # use pip to install Python dependencies of our apps
    pip3 install -I numpy==1.15.4 scipy==1.2.0 netcdf4==1.4.2 six==1.12.0 \
        matplotlib==3.0.2 rasterio==1.0.13 requests==2.21.0

    # download ClawPack and GeoClaw-Landspill
    cd /opt
    git clone --branch v5.5.0 https://github.com/clawpack/clawpack.git
    cd clawpack
    python3 setup.py git-dev 
    cd geoclaw 
    git remote add barbagroup https://github.com/barbagroup/geoclaw.git 
    git fetch barbagroup pull/17/head:pr-17 
    git checkout pr-17

    # set up environment variable for BUILD TIME only
    export FC=gfortran-8
    export CLAW=/opt/clawpack
    export PYTHONPATH=/opt/clawpack

    # download geoclaw-landspill-cases
    cd /opt 
    git clone https://github.com/barbagroup/geoclaw-landspill-cases.git 
    cd geoclaw-landspill-cases 
    python3 setup.py

# =============================================================================
# Command (App): run
# =============================================================================
%apprun run
    exec python $LANDSPILL/run.py "$@"

# =============================================================================
# Command (App): createnc
# =============================================================================
%apprun createnc
    exec python $LANDSPILL/createnc.py "$@"

# =============================================================================
# Command (App): plotdepths
# =============================================================================
%apprun plotdepths
    exec python $LANDSPILL/plotdepths.py "$@"

# =============================================================================
# Command (App): plottopos
# =============================================================================
%apprun plottopos
    exec python $LANDSPILL/plottopos.py "$@"

# =============================================================================
# Command (App): calculatevolume
# =============================================================================
%apprun calculatevolume
    exec python $LANDSPILL/calculatevolume.py "$@"

# =============================================================================
# Default command
# =============================================================================
%runscript
    exec /bin/bash

# =============================================================================
# labels
# =============================================================================
%labels
    Author Pi-Yueh Chuang (pychuang@gwu.edu)
    Version alpha

# =============================================================================
# message shown when using $ singularity run-help {image file}
# =============================================================================
%help

    $ singularity run --app {app} landspill.sif {app arguments}

    App:
        run: run a GeoClaw-Landspill case
        createnc: create NetCDF file for a GeoClaw-Landspill case
        plotdepths: plot depth results for a GeoClaw-Landspill case
        plottopos: plot topo for a GeoClaw-Landspill case
        calculatevolume: calculate total volumes of all AMR levels for a GeoClaw-Landspill case

    To see usage of each app, use
    $ singularity run --app {app} landspill.sif --help
