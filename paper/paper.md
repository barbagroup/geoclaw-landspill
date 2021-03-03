---
title: "geoclaw-landspill: an oil land-spill and overland flow simulator for pipeline rupture events"
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

The package *geoclaw-landspill* builds on the *geoclaw* shallow-water solver to numerically simulate oil land-spills and overland flows that occur during pipeline accidents.
It helps understanding how oil flows above ground after accidental release and to study a pipeline's impact on the environment and economy.
By understanding the impact of a to-be-constructed pipeline, one can choose a pipeline route with the least loss if accidents were to happen.
On the other hand, understanding how oil flows also helps develop rescue teams' deployment strategies and remedy plans for potential accidents.

The package provides a numerical solver for the full shallow-water equations, and post-processing utilities.
The solver is an expanded version of GeoClaw [@Berger2011],
a parallel shallow-water equation solver for tsunami simulations using adaptive mesh refinement (AMR) and finite-volume methods.
We added several new features and modifications to simulate the overland flow of pipeline rupture events, including (citations refer to the details of the adopted models):

* point sources with multi-stage inflow rates to mimic rupture points along a pipeline;
* Lewis Squires Correlation for temperature-dependent flow viscosity [@mehrotra_generalized_1991];
* Darcy-Weisbach friction model with multi-regime coefficient models (laminar, transient, and turbulent regimes) [@Yen2002] and Churchill's model [@churchill_friction-factor_1977];
* in-land waterbody interactions;
* Fingas' evaporation models [@fingas_modeling_2004]; and
* optimizations to improve performance in overland flow simulations.

In addition to the numerical solver, *geoclaw-landspill* is also able to:

* automatically download high-resolution topography and hydrology data, and
* create CF-compliant NetCDF raster files for mainstream GIS software (e.g., QGIS, ArcGIS).

*geoclaw-landspill* includes several examples to showcase its capability to simulate the overland flow on different terrain.

We implemented the core numerical solver and new features using Fortran 2008 to better integrate into the original GeoClaw code.
Other utilities are in Python.
Users can find *geoclaw-landspill* as a Python package on PyPI and install it through pip.
The only dependency that pip does not manage is the Fortran compiler.
Docker images and Singularity images are also available.
They ease the deployment of the solver and simulations to cloud-based high-performance clusters.

# Statement of need

In the US, between 2010 and 2017, an average of 388 hazardous liquid pipeline accidents happened per year.
Half of accidents contaminate soil, and 41% of accidents affect areas with high consequences in either ecology or economy.
Moreover, 85% on average of the released oil was not recovered and kept damaging the environment.
[@belvederesi_statistical_2018]
From the perspective of risk management, while pipelines are unavoidable in modern days, it is necessary to understand how a pipeline may impact the environment if any accidental release happens.
*geoclaw-landspill* serves this purpose.
It provides a free and open-source simulation tool to researchers investigating the danger, risk, and loss posed by potential pipeline accidents.

To our knowledge, *geoclaw-landspill* is the only open-source high-fidelity flow simulator for oil pipeline rupture events.
High fidelity means the results provide more details and accuracy because of high-resolution digital elevation data, fine spatial discretization, and full shallow-water equations.
Commercial products with a similar capability to *geoclaw-landspill* are available [@Zuczek2008; @RPSGroup; @Hydronia; @Gin2012].
Other non-commercial software more or less serving a similar purpose usually relies on simplified models, such as 1D open-channel models, diffusive wave approximation, gravity current models, and gradient-based route selection models [@Hussein2002; @Simmons2003; @Ronnie2004; @farrar_gis_2005; @Guo2006; @Su2017].
Moreover, these non-commercial codes are no longer available or are not open-source.

Another value of *geoclaw-landspill* is that it provides a platform for scholars who study oil flow modeling to implement and test their models.
As the main flow solver is under the BSD 3-Clause License, scholars can add their models to *geoclaw-landspill* freely.

# Past or ongoing research projects using the software

The following conference presentations and posters used previous versions of
*geoclaw-landspill*:

1. Chuang, P.-Y., Thorleifson, T., & Barba, L. A. (2019a, May). GeoClaw-ArcGIS Integration for Advanced Modeling of Overland Hydrocarbon Plumes. *2019 Petroleum GIS Conference Proceedings. 2019 Esri Petroleum GIS Conference, Houston, TX, USA*.

2. Chuang, P.-Y., Thorleifson, T., & Barba, L. A. (2019b, July). Python Workflow for High-Fidelity Modeling of Overland Hydrocarbon Flows with GeoClaw and Cloud Computing. *Proceedings of the 18th Python in Science Conference. 18th Python in Science Conference (SciPy 2019), Austin, TX, USA*.


# Acknowledgments

The project received funding from G2 Integrated Solutions, Houston, TX, USA.

# Author Contributions

Pi-Yueh Chuang developed and is the maintainer of this software.
Tracy Thorleifson was involved in software design, model selection, and software testing.
Lorena A. Barba designed the software specification, development roadmap, and software framework.
She also oversaw the progress of the project.

# Reference
