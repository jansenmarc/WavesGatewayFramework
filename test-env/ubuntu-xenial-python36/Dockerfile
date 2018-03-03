FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev wget
RUN wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz
RUN tar xvf Python-3.6.2.tar.xz
RUN cd Python-3.6.2/ && ./configure && make altinstall
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
