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

RUN \
    apt-get update && \
    apt-get install -y git

COPY entrypoint.sh /entrypoint.sh

RUN \
    chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh"]
