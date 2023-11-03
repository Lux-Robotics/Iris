FROM ubuntu:22.04

RUN apt update && apt -y upgrade

RUN apt install -y --no-install-recommends libpython3.10-dev cmake build-essential gstreamer1.0* ubuntu-restricted-extras libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev pip git

ADD . . 

RUN python3 -m pip install -r requirements.txt

RUN CI=1 python3 -m pip install --upgrade --find-links=https://tortall.net/~robotpy/wheels/2023/raspbian robotpy

RUN git clone https://github.com/opencv/opencv_contrib.git \
    && cd opencv_contrib/ \
    && git checkout 4.x \ 
    && cd .. \ 
    && git clone https://github.com/opencv/opencv.git

RUN cd opencv/ \ 
    && git checkout 4.x\ 
    && mkdir build \ 
    && cd build \ 
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D PYTHON_EXECUTABLE=$(which python3) \
    -D BUILD_opencv_python2=OFF \
    -D CMAKE_INSTALL_PREFIX=$(python3 -c "import sys; print(sys.prefix)") \
    -D PYTHON3_EXECUTABLE=$(which python3) \
    -D PYTHON3_LIBRARY=$(python3 -c "import distutils.sysconfig as sysconfig; import os; print(os.path.join(sysconfig.get_config_var('LIBDIR'), sysconfig.get_config_var('LDLIBRARY')))") \
    -D PYTHON3_INCLUDE_DIR=$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
    -D PYTHON3_PACKAGES_PATH=$(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
    -D OPENCV_EXTRA_MODULES_PATH="../../opencv_contrib/modules" \
    -D WITH_GSTREAMER=ON \
    -D BUILD_EXAMPLES=ON .. \
    && make -j$(nproc) \
    && make install \ 
    && ldconfig

CMD ["python3", "main.py", "--mode=2"]