FROM python:3.9

# Install recent nodejs for bokeh & jsmol-bokeh-extension
# See https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get update && apt-get install -y --no-install-recommends \
  nodejs \
  graphviz \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean all

# Install jsmol
WORKDIR /app

RUN wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
RUN unzip jmol.zip && cd jmol-14.29.22 && unzip jsmol.zip

# Container vars
ENV AIIDA_PATH /app
ENV PYTHONPATH /app

# AiiDA profile vars
ENV AIIDA_PROFILE generic
ENV AIIDADB_HOST host.docker.internal
ENV AIIDADB_PORT 5432
ENV AIIDADB_ENGINE postgresql_psycopg2
ENV AIIDADB_NAME generic_db
ENV AIIDADB_USER db_user
ENV AIIDADB_PASS ""
ENV AIIDADB_BACKEND django
ENV default_user_email info@materialscloud.org


WORKDIR /app/

COPY detail_pyrenemofs ./detail_pyrenemofs
COPY figure_pyrenemofs ./figure_pyrenemofs
COPY pipeline_pyrenemofs ./pipeline_pyrenemofs
COPY select_pyrenemofs ./select_pyrenemofs
RUN ln -s /app/jmol-14.29.22/jsmol ./detail_pyrenemofs/static/jsmol
COPY setup.py ./
RUN pip install -e .
COPY serve-app.sh /opt/

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]
