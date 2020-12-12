# Define global args
ARG FUNCTION_DIR="/function"
ARG RUNTIME_VERSION="3.7"
ARG TAG="latest"

# Choose buster image
FROM conda/miniconda3:${TAG} as base-image

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY app/* ${FUNCTION_DIR}/ 

RUN conda install \
    -c conda-forge \
    -y \
    -q \
    python=${RUNTIME_VERSION} \
    --file ${FUNCTION_DIR}/requirements.txt \
    && pip install awslambdaric

# Multi-stage build: grab a fresh copy of the base image
FROM base-image

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=base-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD [ "app.handler" ]