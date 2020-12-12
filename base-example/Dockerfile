# Dockerfile based on https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

# Define global args
ARG FUNCTION_DIR="/function"
ARG RUNTIME_VERSION="3.6"

# Choose buster image
FROM python:${RUNTIME_VERSION}-buster as base-image

# Install aws-lambda-cpp build dependencies
RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev \

# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
# Simple Example
COPY app/* ${FUNCTION_DIR}/

# Install python dependencies and runtime interface client
RUN python${RUNTIME_VERSION} -m pip install \
                   --target ${FUNCTION_DIR} \
                   --no-cache-dir \
                   awslambdaric \
                   -r ${FUNCTION_DIR}/requirements.txt

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