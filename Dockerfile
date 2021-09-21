FROM onedep_tools_chem_comp

# force using bash shell
SHELL ["/bin/bash", "-c"]

# access to content server
ARG CS_USER
ARG CS_PW
ARG CS_URL

# setup paths
ENV VENV=/venv
ENV PATH=$VENV/bin:$ONEDEP_TOOLS_ROOT/bin:$PATH

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