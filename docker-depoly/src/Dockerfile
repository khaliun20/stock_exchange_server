FROM ubuntu:20.04
RUN apt-get update && apt-get install libpq-dev python-dev python3-pip -y
RUN mkdir hw4
WORKDIR /hw4
ADD . /hw4
RUN pip3 install -r /hw4/requirements.txt
RUN chmod +x runserver.sh