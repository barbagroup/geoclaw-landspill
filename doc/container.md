# Containers: Docker and Singularity

We provide Docker images on Docker Hub and Singularity images on Singularity Hub.

---------------
## Docker usage

Pull the Docker image through:
```
$ docker pull barbagroup/landspill:<version>
```

Replace `<version>` with a desired version string. For example, `v1.0.dev1`.

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

Interested users can build Docker image locally using the Dockerfiles in folder
`Dockerfiles`.

------------------------------------------------------------------------
## Singularity usage (Singularity version >= 3.4)

On many HPC clusters or supercomputers, Docker is not available due to
security concerns, and [Singularity](https://www.sylabs.io/singularity/) is the 
only container technology available. 

To pull a Singularity image with tag `<version>` (e.g., `v1.0.dev1`) and save to
a local image file, do
```
$ singularity pull lanspill-<version>.sif library://barbagroup/geoclaw-landspill:<version>
```

One can get into the shell of a Singularity container and run cases as described
in the section of Docker usage. Also, the provided Singularity image exposes
`geoclaw-landspill`'s subcommands as apps. So users can also do something like
```
$ singularity run --app run landspill-<version>.sif <case on the host>
```

The `--app run` means Singularity will call the `run` subcommand of the
`geoclaw-landspill` in the `landspill-<version>.sif` image. Singularity
automatically maps some folders on the host into a container. For example, a
user's `$HOME`. So if there's a case at a user's `$HOME`, such as
`$HOME/smaple_case`, then the user can do
```
$ singularity run --app run landspill-<version>.sif $HOME/sample_case
```
without copying case data into the container. Please refer to Singularity's
documentation for more details.

To see other available apps of the image `landspill-<version>.sig`:
```
$ singularity run-help landspill.sif
```

Interested users can build Singularity images locally with the configuration
files in folder `Singularityfiles`.
