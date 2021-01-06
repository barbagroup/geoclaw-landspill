# Containers: Docker and Singularity

We provide Docker images on Docker Hub and Singularity images on Singularity Hub.

---------------
## Docker usage

Pull the Docker image through:
```
$ docker pull barbagroup/landspill:<version>
```

Replace `<version>` with a desired version string. For example, `v1.0.dev1`. To
see all tags/versions, check the
[Docker Hub page](https://hub.docker.com/repository/docker/barbagroup/landspill).

To get into the shell of a Docker container:
```
$ docker run -it --name landspill barbagroup/landspill:<version>
```
Once getting into the shell, the example cases are under
`~/geoclaw-landspill-cases`. *geoclaw-landspill* is ready to use. For example,
in the shell of the Docker container, run the `utah-flat-maya` case with
```
$ geoclaw-landspill run ~/geoclaw-landspill-cases/utah-flat-maya
```

Interested users can build Docker image locally using the Dockerfile in folder
`Dockerfiles`. For example, to build an image with version `1.0.dev1` (the
corresponding tag is `v1.0.dev1`):
```
$ cd Dockerfiles
$ docker build \
    --tag "my_image" --build-arg "VER=v1.0.dev1" --target production
    --file Dockerfile .
```
`my_image` will be the image name in the local Docker registry.

------------------------------------------------------------------------
## Singularity usage (Singularity version >= 3.4)

On many HPC clusters or supercomputers, Docker is not available due to
security concerns, and [Singularity](https://www.sylabs.io/singularity/) is the 
only container technology available. 

To pull a Singularity image with tag `<version>` (e.g., `v1.0.dev1`) and save to
a local image file, do
```
$ singularity pull lanspill-<version>.sif shub://barbagroup/geoclaw-landspill:<version>
```

One can get into the shell of a Singularity container and run cases as described
in the section of Docker usage. Also, the Singularity image can be used as an
executable, which is equivalent to the executable `geoclaw-landspill`. For
example, to run a case:
```
$ landspill-<version>.sif run <case on the host>
```

Or, to see the help of subcommand `plotdepth`:
```
$ landspill-<version>.sif plotdepth --help
```

Alternatively, to run a Singularity image with the regular approach and, for
example, to create a NetCDF file:
```
$ singularity run landspill-<version>.sif createnc <path to a case>
```

Singularity automatically maps some folders on the host into a container. For
example, a user's `$HOME`. So if there's a case at a user's `$HOME`, such as
`$HOME/smaple_case`, then the user can do
```
$ landspill-<version>.sif run $HOME/sample_case
```
without copying case data into the container. Please refer to Singularity's
documentation for more details.

Interested users can build Singularity images locally with the configuration
files in folder `Singularityfiles`. Currently, there is one Singularity file
per release version:
```
# singularity build <the name of the image> Singularity.<version>
```
`<the name of the image>` is whatever name a user would like to use for his/her
image.
