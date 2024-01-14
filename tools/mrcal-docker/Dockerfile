FROM ubuntu:22.04

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Update the package repository and install the necessary packages
RUN apt update && apt install -y --no-install-recommends \
    mrcal \
    libmrcal-dev \
    python3-mrcal \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Switch back to interactive
ENV DEBIAN_FRONTEND=

# Ensure scripts are executable
COPY scripts/ /scripts
RUN chmod +x /scripts/*

ENTRYPOINT ["tail", "-f", "/dev/null"]
