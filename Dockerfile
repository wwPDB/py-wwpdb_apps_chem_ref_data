FROM centos:7

RUN yum group install -y "Development Tools"
RUN yum install -y epel-release
RUN yum -y install openssl-devel bzip2-devel libffi-devel
RUN yum -y install git cmake gcc gcc-c++ wget libarchive bison flex gcc-gfortran
RUN yum -y install eigen3-devel zlib-devel libxml2-devel swig cairo-devel
RUN yum -y install mariadb mariadb-devel subversion cvs tcsh

# remove any caching
RUN yum clean all

# install inchi - using CentOS 7 rpm (works in both CentOS 7 and CentOS 8
RUN wget -O inchi.rpm https://download-ib01.fedoraproject.org/pub/epel/7/x86_64/Packages/i/inchi-1.0.4-4.el7.x86_64.rpm
RUN rpm -Uvh inchi.rpm

# eigen2
RUN wget -O eigen-2.0.17.tar.gz https://gitlab.com/libeigen/eigen/-/archive/2.0.17/eigen-2.0.17.tar.gz
RUN tar -xvf eigen-2.0.17.tar.gz
RUN cd eigen-2.0.17 \
    && mkdir builddir \
    && cd builddir \
    && cmake -DCMAKE_INSTALL_PREFIX=/eigen-2-0.17-install   /eigen-2.0.17 \
    && make install


# install openbabel - compatible with CentOS 7 and CentOS 8
RUN wget -O openbabel-2.3.2.tar.gz https://github.com/openbabel/openbabel/archive/refs/tags/openbabel-2-3-2.tar.gz
RUN tar -xvf openbabel-2.3.2.tar.gz
RUN cd openbabel-openbabel-2-3-2 \
    && cat ./include/openbabel/shared_ptr.h | sed -e 's/__GNUC__ == 4/__GNUC__ >= 4/g' > ./include/openbabel/shared_ptr.h.tmp \
    && mv ./include/openbabel/shared_ptr.h ./include/openbabel/shared_ptr.h__orig \
    && mv ./include/openbabel/shared_ptr.h.tmp ./include/openbabel/shared_ptr.h \
    && cat ./CMakeLists.txt | sed -e '0,/if(NOT MSVC)/s//set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -Wno-error -std=c++03")\nset(CMAKE_C_FLAGS  "${CMAKE_C_FLAGS} -Wno-error")\n\nif(NOT MSVC)/g' > CMakeLists.txt.tmp \
    && mv ./CMakeLists.txt ./CMakeLists.txt__orig \
    && mv ./CMakeLists.txt.tmp ./CMakeLists.txt
RUN mkdir build \
    && cd build \
    && cmake ../openbabel-openbabel-2-3-2 \
      -DPYTHON_BINDINGS=OFF \
      -DBUILD_GUI=OFF \
      -DEIGEN2_INCLUDE_DIR=/eigen-2-0.17-install \
    && make -j 2 \
    && make install

# add additional library paths
RUN echo /usr/local/lib > /etc/ld.so.conf.d/usrlocal.conf
RUN ldconfig

# python 3.8
ENV PYTHON_VERSION=3.8.9
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
RUN tar -xvf Python-$PYTHON_VERSION.tgz
RUN cd Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations  \
    && make altinstall

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

# build chem comp pack in /tools
ENV BUILD_DIR=/tools/build_dir
ENV DISTRIB_DIR=/tools/distrib_dir
ENV DISTRIB_SOURCE_DIR=/tools/distrib_source
ENV PACKAGE_DIR=/tools/packages
RUN git clone git@github.com:wwPDB/onedep-build.git /src/onedep-build
RUN . /src/onedep-build/utils/pkg-utils-v2.sh \
    && . /src/onedep-build/v-5200/packages/all-packages.sh \
    && pkg_build_openeye_c7 \
    && pkg_build_chem_comp_pack

# setup a venv
ENV VENV=/venv
ENV PATH=$VENV/bin:$PATH

# setup venv
RUN python3.8 -m venv $VENV
RUN pip install --no-cache-dir --upgrade setuptools pip
RUN pip config --site set global.no-cache-dir false
RUN pip install wheel
RUN pip install wwpdb.utils.config

# copy this package
WORKDIR /workdir
COPY . .

RUN pip install .