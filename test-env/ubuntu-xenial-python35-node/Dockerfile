FROM ubuntu:xenial

RUN apt-get update
RUN apt-get install -y python3.5 python3.5-dev wget apt-transport-https build-essential libssl-dev curl python3-pip python3-setuptools
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get install -y google-chrome-stable nodejs
