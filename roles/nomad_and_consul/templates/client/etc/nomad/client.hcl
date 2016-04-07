data_dir = "{{ nomad_consul_server_datadir }}"
region = "{{ nomad_consul_client_region }}"
datacenter = "{{ nomad_consul_client_datacenter }}"

client {
  enabled = true

  # The server cluster we should connect to
  servers = {{ hostvars | server_group_ip_map_v2(nomad_server_list, nomad_client_bind_iface) | to_json }}
  
  # Set up some options for the client
  options {
    #consul.token = "axAcg446arwemBuud5hizg=u"
     "driver.raw_exec.enable" = "1"
  }

  # KVM guests using virtio network driver can't dynamically discover network speed
  # so we set it here.
  # network_speed = 10000		# 10 Gbps

  # Reserve resources that Nomad scheduler should leave alone
  reserved {
    cpu = 200		# Keep 200 MHz for Nomad
    memory = 64		# Keep 64 MB for Nomad
    disk = 512		# Keep 512 MB for Nomad
    reserved_ports = "22,25,80,123,5666,8500-8600,9102"
  }
}
