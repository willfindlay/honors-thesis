FROM ubuntu:bionic as intermediate

MAINTAINER William Findlay <williamfindlay@cmail.carleton.ca>

RUN apt-get -qq update && \
    apt-get -y install git

#RUN git clone https://github.com/HousedHorse/bcc
RUN git clone https://github.com/iovisor/bcc

FROM ubuntu:bionic

# install pre-reqs
RUN apt-get -qq update && \
    apt-get -y install bison build-essential cmake flex git libedit-dev \
    libllvm6.0 llvm-6.0-dev libclang-6.0-dev python zlib1g-dev libelf-dev \
    python3-pip libgl1-mesa-glx qt5-default sudo
RUN pip3 install pyside2

# install bcc
COPY --from=intermediate /bcc /root/bcc
WORKDIR /root/bcc
RUN git checkout fed32105329e4295cf1e6acb87c365f76c2e64c3
RUN mkdir build && cd build && \
    cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_CMD=python3 && \
    make && \
    make install

# install ebpH
RUN mkdir -p /app
WORKDIR /app
COPY . /app
