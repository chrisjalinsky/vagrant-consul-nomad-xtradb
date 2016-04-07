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
# echo Fetching Consul...
# cd /tmp/
# wget https://releases.hashicorp.com/consul/{{ nomad_consul_version }}/consul_{{ nomad_consul_version }}_linux_amd64.zip -O consul.zip
# echo Installing Consul...
# unzip consul.zip
# sudo chmod +x consul
# sudo mv consul /usr/bin/consul
# Install Docker
echo deb https://apt.dockerproject.org/repo ubuntu-`lsb_release -c | awk '{print $2}'` main | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo apt-get update
sudo apt-get install -y docker-engine
# Restart docker to make sure we get the latest version of the daemon if there is an upgrade
sudo service docker restart
# Make sure we can actually use docker as the {{ nomad_consul_docker_user }} user
sudo usermod -aG docker {{ nomad_consul_docker_user }}
# Setup Nomad for development
cd {{ nomad_git_repo_path }} && make bootstrap
# Install rkt
#bash {{ nomad_install_script_path }}/install_rkt.sh
# CD into the nomad working directory when we login to the VM
#grep "cd {{ nomad_git_repo_path }}" ~/.profile || echo "cd {{ nomad_git_repo_path }}" >> ~/.profile

# Just a crude check
echo "YER_INSTALLATION_IS_COMPLETE"