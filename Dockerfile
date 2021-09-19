FROM centos:7

RUN yum group install -y "Development Tools"
RUN yum install -y epel-release
RUN yum -y install openssl-devel bzip2-devel libffi-devel
RUN yum -y install git cmake gcc gcc-c++ wget libarchive bison flex gcc-gfortran
RUN yum -y install eigen3-devel zlib-devel libxml2-devel swig cairo-devel
RUN yum -y install mariadb mariadb-devel subversion cvs tcsh

# remove any caching
RUN yum clean all

# python 3.8
ENV PYTHON_VERSION=3.8.9
RUN wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
RUN tar -xvf Python-$PYTHON_VERSION.tgz
RUN cd Python-$PYTHON_VERSION; ./configure --enable-optimizations; make altinstall

# force using bash shell
SHELL ["/bin/bash", "-c"]

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