FROM ubuntu:20.04

# Generate and Set locals
# https://stackoverflow.com/questions/28405902/how-to-set-the-locale-inside-a-debian-ubuntu-docker-container#38553499
RUN \
    apt-get update && \
    apt-get install locales --yes && \
    # install locales-all?
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LC_ALL="en_US.UTF-8" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US:en" \
    TZ="Europe/Berlin" \
    DEBIAN_FRONTEND="noninteractive"

# Install Python
RUN \
    apt-get update && apt-get install -y python3 python3-pip curl software-properties-common && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip


# Install Docker in Container
RUN \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable" && \
    apt-get update -y && \
    apt-get install -y docker-ce=5:19.03.13~3-0~ubuntu-focal

RUN \ 
    pip install pytest

# Install Universal-Build
# RUN \
#     pip install -e git+https://github.com/ml-tooling/universal-build.git


COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh"]