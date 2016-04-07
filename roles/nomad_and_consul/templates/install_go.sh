#!/bin/bash

# Setup go, for development of Nomad
SRCROOT="/opt/go"
SRCPATH="{{ nomad_git_repo_path }}"
# Get the ARCH
ARCH=`uname -m | sed 's|i686|386|' | sed 's|x86_64|amd64|'`
# Install Go
cd /tmp
wget -q https://storage.googleapis.com/golang/go1.6.linux-${ARCH}.tar.gz
tar -xf go1.6.linux-${ARCH}.tar.gz
sudo mv go $SRCROOT
sudo chmod 775 $SRCROOT
sudo chown {{ nomad_consul_docker_user }}:{{ nomad_consul_docker_group }} $SRCROOT
# Setup the GOPATH; even though the shared folder spec gives the working
# directory the right user/group, we need to set it properly on the
# parent path to allow subsequent "go get" commands to work.
sudo mkdir -p $SRCPATH
sudo chown -R {{ nomad_consul_docker_user }}:{{ nomad_consul_docker_group }} $SRCPATH 2>/dev/null || true
# ^^ silencing errors here because we expect this to fail for the shared folder
cat <<EOF >/tmp/gopath.sh
export GOPATH="$SRCPATH"
export GOROOT="$SRCROOT"
export PATH="$SRCROOT/bin:$SRCPATH/bin:\$PATH"
EOF
sudo mv /tmp/gopath.sh /etc/profile.d/gopath.sh
sudo chmod 0755 /etc/profile.d/gopath.sh
source /etc/profile.d/gopath.sh