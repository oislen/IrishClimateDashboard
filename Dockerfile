# get base image
FROM python:3.12

# set environment variables
ENV user=ubuntu
ENV DEBIAN_FRONTEND=noninteractive
# set python version
ARG PYTHON_VERSION="3.12"
ENV PYTHON_VERSION=${PYTHON_VERSION}

# install required software and programmes for development environment
RUN apt-get update
RUN apt-get install -y apt-utils vim curl wget unzip tree htop adduser
# install trivy image vulnerability patches
RUN apt-get install -y imagemagick=8:7.1.1.43+dfsg1-1+deb13u5
RUN apt-get install -y libssl-dev=3.5.4-1~deb13u2
RUN apt-get install -y libpq-dev=17.8-0+deb13u1
RUN apt-get install -y libpng-dev=1.6.48-1+deb13u3 libpng16-16t64=1.6.48-1+deb13u3
RUN apt-get install -y linux-libc-dev=6.12.73-1

# set up home environment
RUN adduser ${user}
RUN mkdir -p /home/${user} && chown -R ${user}: /home/${user}

# clone git repo
COPY . /home/${user}/IrishClimateDashboard
# set working directory
WORKDIR /home/${user}/IrishClimateDashboard

# install required python packages
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv sync

EXPOSE 5006
CMD ["uv", "run", "bokeh", "serve","dashboard/bokeh_dash_app.py"]