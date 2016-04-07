VAGRANTFILE_API_VERSION = "2"
BOX = "trusty64"

base_dir = File.expand_path(File.dirname(__FILE__))

NETWORK_SUBNET1 = "172.136.9"
NETWORK_SERVER_DOMAIN = "cluster"
NUM_SERVER_HOSTS = 3
NUM_CLIENT_HOSTS = 3
SERVER_HOST_IPS_START = 55
CLIENT_HOST_IPS_START = 105
HOST_MEMORY = 2048
CLIENT_MEMORY = 2048
HOST_CPU = 1
CLIENT_CPU = 1

ansible_provision = proc do |ansible|
  ansible.playbook = 'site.yml'
  ansible.groups = {
    'server_hosts'    => (1..NUM_SERVER_HOSTS).map { |j| "consul#{j}.#{NETWORK_SERVER_DOMAIN}" },
    'client_hosts'    => (1..NUM_CLIENT_HOSTS).map { |j| "client#{j}.#{NETWORK_SERVER_DOMAIN}" },
    'all:children'      => ["server_hosts", "client_hosts"],
  }

  ansible.extra_vars = {
    cluster_network: "#{NETWORK_SUBNET1}.0/24",
  }
  ansible.limit = 'all'
  ansible.verbose = "v"
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.ssh.insert_key = false
  config.vm.box = BOX

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :machine
    config.cache.enable :apt
  end

  (1..NUM_CLIENT_HOSTS).each do |i|
    config.vm.define "client#{i}.#{NETWORK_SERVER_DOMAIN}" do |de|
      de.vm.hostname = "client#{i}.#{NETWORK_SERVER_DOMAIN}"
      de.vm.network :private_network, ip: "#{NETWORK_SUBNET1}.#{CLIENT_HOST_IPS_START + i}"

      de.vm.provider :virtualbox do |vb|
        vb.customize ['modifyvm', :id, '--memory', "#{HOST_MEMORY}"]
        vb.customize ['modifyvm', :id, '--cpus', "#{HOST_CPU}"]
      end

      de.vm.provider :vmware_fusion do |v|
        v.vmx['memsize'] = "#{HOST_MEMORY}"
      end

      de.vm.provider "libvirt" do |lv|
        lv.uri = 'qemu+unix:///system'
        lv.driver = 'kvm'
        lv.memory = CLIENT_MEMORY
        lv.cpus = CLIENT_CPU
      end
    end
  end

  (1..NUM_SERVER_HOSTS).each do |i|
    config.vm.define "consul#{i}.#{NETWORK_SERVER_DOMAIN}" do |de|
      de.vm.hostname = "consul#{i}.#{NETWORK_SERVER_DOMAIN}"
      de.vm.network :private_network, ip: "#{NETWORK_SUBNET1}.#{SERVER_HOST_IPS_START + i}"
      de.vm.network "forwarded_port", guest: 8500, host: 8500 + i, auto_correct: true

      de.vm.provider :virtualbox do |vb|
        vb.customize ['modifyvm', :id, '--memory', "#{HOST_MEMORY}"]
        vb.customize ['modifyvm', :id, '--cpus', "#{HOST_CPU}"]
      end

      de.vm.provider :vmware_fusion do |v|
        v.vmx['memsize'] = "#{HOST_MEMORY}"
      end

      de.vm.provider "libvirt" do |lv|
        lv.uri = 'qemu+unix:///system'
        lv.driver = 'kvm'
        lv.memory = HOST_MEMORY
        lv.cpus = HOST_CPU
        #lv.storage :file, :size => '10G', :type => 'raw'#, :device => "sdb1", :path => "aero#{i}sdb1", :allow_existing => true
      end

      de.vm.provision 'ansible', &ansible_provision if i == (NUM_SERVER_HOSTS)
    end
  end
end