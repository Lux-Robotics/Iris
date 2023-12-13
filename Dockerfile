FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update ubuntu package lists
RUN apt update

# Install build dependencies
RUN apt install -y --no-install-recommends libpython3.10-dev cmake build-essential

# Install gstreamer
RUN apt install -y --no-install-recommends gstreamer1.0* ubuntu-restricted-extras libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Install utilities
RUN apt install -y --no-install-recommends pip g++ wget unzip

# Install numpy
RUN python3 -m pip install numpy

# Download and uncompress opencv files
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.x.zip \
    && wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.x.zip \
    && unzip opencv.zip \
    && unzip opencv_contrib.zip

# Build opencv
RUN cd opencv-4.x/ \
    && mkdir build \
    && cd build \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D PYTHON_EXECUTABLE=$(which python3) \
    -D BUILD_opencv_python2=OFF \
    -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
    -D PYTHON3_EXECUTABLE=$(which python3) \
    -D PYTHON3_LIBRARY=$(python3 -c "import distutils.sysconfig as sysconfig; import os; print(os.path.join(sysconfig.get_config_var('LIBDIR'), sysconfig.get_config_var('LDLIBRARY')))") \
    -D PYTHON3_INCLUDE_DIR=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
    -D PYTHON3_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
    -D OPENCV_EXTRA_MODULES_PATH="../../opencv_contrib-4.x/modules/aruco" \
    -D WITH_GSTREAMER=ON \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D BUILD_opencv_apps=OFF .. \
    && make -j$(nproc) \
    && make install \
    && ldconfig

# Clean up build files
RUN rm -rf opencv-4.x/ opencv_contrib-4.x/

# Set the working directory inside the container
WORKDIR /app

# Install python libraries
ADD requirements.txt /app
RUN python3 -m pip install -r requirements.txt
RUN CI=1 python3 -m pip install --upgrade --find-links=https://tortall.net/~robotpy/wheels/2023/raspbian 'robotpy[apriltag]'

# Add project files
ADD . /app

CMD ["python3", "main.py"]
