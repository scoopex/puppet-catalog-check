#!/bin/bash

SDIR="$(dirname $(readlink -f $0))"
RELEASE="$1"

echo "PUPPET RELEASE: $RELEASE"
set -x
set -e

apt-get update
apt-get install curl lsb-release vim -y

REL="$(lsb_release -c -s)"

rm -rf /tmp/setup-ubuntu/
mkdir /tmp/setup-ubuntu
cd /tmp/setup-ubuntu
curl "https://apt.puppetlabs.com/puppetlabs-release-pc1-${REL}.deb" > puppetlabs-release-pc1-${REL}.deb
dpkg -i puppetlabs-*.deb
apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get install puppetdb-termini=4.3.2-1puppetlabs1 -y
apt-get install puppet-agent librarian-puppet git python3-pip trocla -y
apt-get install python3-nose python3-coverage -y
apt-get install jq -y

ln -snf /opt/puppetlabs/bin/puppet /usr/local/sbin/puppet

cd /etc/puppetlabs/puppet
rm -f *
cp -av /puppet-catalog-check/etc/* /etc/puppetlabs/puppet/

mkdir -p /etc/puppet/environments
mkdir -p /etc/puppetlabs/code
rm -rf /etc/puppetlabs/code/environments
ln -s /etc/puppet/environments /etc/puppetlabs/code/environments

rm -rf /etc/puppetlabs/puppet/ssl
ln -snf  /puppet-catalog-check/etc/puppet-ssl ssl
gem install r10k
pip3 install pypuppetdb
pip3 install json-delta

apt-get remove python3-pip -y
apt-get autoremove -y

echo "source /puppet-catalog-check/share/scripts/env.sh" >> /root/.bashrc
mkdir /root/.ssh
chmod 700 /root/.ssh
cp /puppet-catalog-check/etc/id_rsa /root/.ssh/id_rsa
cp /puppet-catalog-check/etc/known_hosts /root/.ssh/known_hosts
chmod 700 /root/.ssh/id_rsa /root/.ssh/known_hosts
