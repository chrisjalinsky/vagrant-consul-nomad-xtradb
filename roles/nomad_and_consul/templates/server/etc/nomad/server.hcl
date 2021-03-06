bind_addr = "{{ nomad_server_bind_address }}"
data_dir = "{{ nomad_consul_server_datadir }}"
region = "{{ nomad_consul_server_region }}"
datacenter = "{{ nomad_consul_server_datacenter }}"

advertise {
  # We need to specify our host's IP because we can't
  # advertise 0.0.0.0 to other nodes in our cluster.
  rpc = "{{ nomad_server_bind_address }}:4647"
}

server {
  enabled = true
  bootstrap_expect = {{ nomad_server_list | length }}
  start_join = {{ hostvars | server_group_ip_map_v2(nomad_server_list, nomad_server_bind_iface) | to_json }}
}