FROM centos:7

RUN yum group install -y "Development Tools"
RUN yum install -y epel-release
RUN yum -y install openssl-devel bzip2-devel libffi-devel
RUN yum -y install git cmake gcc gcc-c++ wget libarchive bison flex gcc-gfortran
RUN yum -y install eigen3-devel zlib-devel libxml2-devel swig cairo-devel
RUN yum -y install mariadb mariadb-devel subversion cvs tcsh
RUN yum -y install python2 python2-devel

# remove any caching
RUN yum clean all

# force using bash shell
SHELL ["/bin/bash", "-c"]

# setup access to private repositories using SSH_PRIVATE_KEY
ARG SSH_PRIVATE_KEY
RUN mkdir ~/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" | tr -d '\r' > ~/.ssh/id_rsa
RUN chmod 600 ~/.ssh/id_rsa
RUN ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub
# enable access to github.com
RUN touch ~/.ssh/known_hosts
RUN ssh-keyscan github.com >> ~/.ssh/known_hosts

# access to content server
ARG CS_USER
ARG CS_PW
ARG CS_URL

# setup paths
ENV VENV=/venv
ENV PATH=$VENV/bin:/tools/bin:$PATH

# build chem comp pack in /tools
ENV ONEDEP_TOOLS_ROOT=/onedep_tools
ENV BUILD_DIR=$ONEDEP_TOOLS_ROOT/build_dir
ENV DISTRIB_DIR=$ONEDEP_TOOLS_ROOT/distrib_dir
ENV DISTRIB_SOURCE_DIR=$ONEDEP_TOOLS_ROOT/distrib_source
ENV PACKAGE_DIR=$ONEDEP_TOOLS_ROOT/packages
ENV TOOLS_DIR=$ONEDEP_TOOLS_ROOT
ENV PREFIX=$ONEDEP_TOOLS_ROOT

# make directories for use
RUN mkdir -p $BUILD_DIR/INSTALL_FLAGS \
    && mkdir -p $DISTRIB_DIR \
    && mkdir -p $DISTRIB_SOURCE_DIR \
    && mkdir -p $PACKAGE_DIR

RUN git clone git@github.com:wwPDB/onedep-build.git /src/onedep-build
RUN . /src/onedep-build/utils/pkg-utils-v2.sh \
    && . /src/onedep-build/v-5200/packages/all-packages.sh \
    && pkg_build_inchi \
    && pkg_build_cmake \
    && pkg_build_eigen3 \
    && pkg_build_python27 \
    && pkg_build_python3

# update root python2 packages
RUN pip install --upgrade pip~=20.2
RUN pip install --upgrade setuptools
RUN pip install wheel
RUN pip install scons

RUN . /src/onedep-build/utils/pkg-utils-v2.sh \
    && . /src/onedep-build/v-5200/packages/all-packages.sh \
    && pkg_build_openbabel223 \
    && pkg_build_openbabel232_nopython \
    && pkg_build_scons \
    && pkg_build_openeye_c7 \
    && pkg_build_chem_comp_pack

# setup venv
RUN python3 -m venv $VENV
RUN pip install --no-cache-dir --upgrade setuptools pip
RUN pip config --site set global.no-cache-dir false
RUN pip install wheel
RUN pip install wwpdb.utils.config

# copy this package
WORKDIR /src/chem_ref_data
COPY . .

RUN pip install .