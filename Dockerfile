# get base image
FROM ubuntu:20.04

# set environment variables
ENV user=ubuntu
ENV DEBIAN_FRONTEND=noninteractive

# install required software and programmes for development environment
RUN apt-get update 
RUN apt-get install -y apt-utils vim curl wget unzip git python3 python3-pip tree htop

# set up home environment
RUN useradd ${user}
RUN mkdir -p /home/${user} && chown -R ${user}: /home/${user}

# clone git repo
RUN git clone https://github.com/oislen/IrishClimateDashboard.git /home/ubuntu/IrishClimateDashboard

# install required python packages
COPY requirements.txt /tmp/
RUN apt-get install -y python3 python3-venv python3-pip
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/python3 -m pip install -r /tmp/requirements.txt

WORKDIR /home/${user}/IrishClimateDashboard/scripts
CMD ["bokeh", "serve","bokeh_dash_app.py"]