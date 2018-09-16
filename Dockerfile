# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices
#
FROM ubuntu:16.04
MAINTAINER ms@256bit.org
ARG puppetrelease=4

ADD share /puppet-catalog-check/share
ADD bin /puppet-catalog-check/bin
ADD etc /puppet-catalog-check/etc
RUN bash /puppet-catalog-check/share/scripts/setup-puppet-env.sh ${puppetrelease}
