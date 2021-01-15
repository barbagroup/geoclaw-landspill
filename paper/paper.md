---
title: "geoclaw-landspill: oil land-spill and overland flow simulator for pipeline rupture events"
tags:
  - shallow-water-equations
  - overland-flow
  - land-spill
  - pipeline
  - geoclaw
authors:
  - name: Pi-Yueh Chuang
    orcid: 0000-0001-6330-2709
    affiliation: 1
  - name: Tracy Thorleifson
    affiliation: 2
  - name: Lorena A. Barba
    orcid: 0000-0001-5812-2711
    affiliation: 1
affiliations:
  - name: Department of Mechanical and Aerospace Engineering, the George Washington University, Washington, DC, USA
    index: 1
  - name: G2 Integrated Solutions, Houston, TX, USA
    index: 2
date: 15 January 2021
bibliography: paper.bib
---

# Summary

*geoclaw-landspill* is a package for simulations of oil land-spill and overland flow that occurs during pipeline accidents.
It serves as a tool for researchers to study a pipeline's risk to the environment and economy.
On the other hand, it also helps studies of deployment strategies of rescue teams and remedy plans for potential pipeline accidents. 

The package provides a numerical solver that solves full shallow-water equations and post-processing utilities.
The numerical solver is an expanded version of GeoClaw.
GeoClaw is a parallel shallow-water equation solver for tsunami simulations using adaptive mesh refinement (AMR) and finite-volume methods.
We added several new features and modifications to simulate the overland flow of pipeline rupture events, including:

* point sources with multi-stage inflow rates to mimic rupture points along a pipeline,
* temperature-dependent flow properties,
* Darcy-Weisbach friction model with several coefficient models,
* in-land waterbody interactions,
* evaporation models, and
* optimizations to improve performance in overland flow simulations.

Beyond the numerical solver, *geoclaw-landspill* is also able to:

* automatically download high-resolution topography and hydrology data, and
* create CF-compliant NetCDF raster files for mainstream GIS software (e.g., QGIS, ArcGIS).

*geoclaw-landspill* includes several examples to showcase its capability to simulate the overland flow on different terrain.

We implemented the core numerical solver and new features using Fortran 2008 to better integrate into the original GeoClaw code.
Other utilities are in Python.
Users can find *geoclaw-landspill* as a Python package on PyPI and install it through `pip`.
The only dependency that pip does not manage is the Fortran compiler.
Docker images and Singularity images are also available.
They ease the deployment of the solver and simulations to cloud-based high-performance clusters.

# Statement of need

In the US, an average of 388 hazard liquid pipeline accidents happened per year between 2010 and 2017, causing a 140-million-dollar environment-related cost per year.
50% of accidents contaminate soil, and 41% of accidents affect areas with high consequences in either ecology or economy. [@belvederesi_statistical_2018]
From the perspective of risk management, while pipelines are unavoidable in modern days, it is necessary to understand how a pipeline may impact the environment if any accidents happen.
*geoclaw-landspill* serves this purpose.

To our knowledge, *geoclaw-landspill* is the only open-source high-fidelity flow simulator for oil pipeline rupture events.
High fidelity means the results provide more details and accuracy because of high-resolution digital elevation data, fine spatial discretization, and full shallow-water equations.
Commercial products with a similar capability to *geoclaw-landspill* are available [@Zuczek2008; @RPSGroup; @Hydronia; @Gin2012].
Other non-commercial software for land-spill modeling usually relies on simplified models, such as 1D open-channel models, diffusive wave approximation, gravity current models, and gradient-based route selection models [@Hussein2002; @Simmons2003; @Ronnie2004; @farrar_gis_2005; @Guo2006; @Su2017].
Moreover, these non-commercial codes are either non-exist in modern days or are not open-source. 

# Acknowledgments

The project received funding from G2 Integrated Solutions.

# Author Contributions

Pi-Yueh Chuang developed and is the maintainer of this software.
Tracy Thorleifson was involved in the decision-making process of the software design and tested the software.
Lorena A. Barba was the principal investigator and oversaw the progress of the project. 

# Reference
