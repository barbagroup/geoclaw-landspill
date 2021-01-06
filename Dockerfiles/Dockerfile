# vim:ft=dockerfile

# Multi-stage build stage 0: build
# ================================
FROM ubuntu:focal as builder

# change default shell from sh to bash
SHELL ["/bin/bash", "-c"]

# create basic working environment
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone \
 && apt update && apt -y full-upgrade \
 && apt install -y --no-install-recommends git ca-certificates gfortran python3 python3-pip

# cmd argument to control which version to checkout
ARG VER

# clone geoclaw-landspill dev branch
RUN git clone --branch ${VER} --recurse-submodules https://github.com/barbagroup/geoclaw-landspill.git

# install dependencies for building binary from pip
RUN cd /geoclaw-landspill && pip3 install -r requirements-build.txt

# build binary wheel
RUN cd /geoclaw-landspill && python3 setup.py bdist_wheel --build-type RELEASE


# Multi-stage build stage 1: runtime image
# =========================================
FROM ubuntu:focal as production
LABEL maintainer="Pi-Yueh Chuang <pychuang@gwu.edu>"

# copy the wheel file and example cases
COPY --from=builder /geoclaw-landspill/dist/geoclaw_landspill-*.whl /root
COPY --from=builder /geoclaw-landspill/cases /root/cases

# add a new non-root user and move example case folders
RUN useradd -U -m -u 9999 -s /bin/bash landspill \
 && mv /root/cases /home/landspill/geoclaw-landspill-cases \
 && chown landspill:landspill -R /home/landspill/geoclaw-landspill-cases

# create runtime environment
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo UTC > /etc/timezone \
 && apt update && apt -y full-upgrade \
 && apt install -y --no-install-recommends libgfortran5 libgomp1 python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# install geoclaw-landspill
RUN pip3 install /root/geoclaw_landspill-*.whl && rm -f /root/geoclaw_landspill-*.whl

# set up necessary runtime environment variables
ENV MPLBACKEND="agg"

# change default user to landspill and corresponding work directory
USER landspill
WORKDIR /home/landspill

# default command
CMD ["/bin/bash"]
