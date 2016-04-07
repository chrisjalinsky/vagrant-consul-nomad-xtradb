def hash_to_tuples(h):
    return h.items()

def hash_keys(h):
    return h.keys()

def hash_values(h):
    return h.values()

def zipped_hash(h, key, item):
    ret = []
    for el in h:
        if h[el].has_key(item):
            for subel in h[el][item]:
                ret.append({"key" : h[el][key], "value" : subel })
    return ret

def server_group_filter(d,l,i):
    result = []
    if len(l) > 0:
        for item in l:
            if item != i:
                try:
                    ip_addr = d[item]['ansible_eth1']['ipv4']['address']
                    if ip_addr:
                        result.append(ip_addr)
                except:
                    pass
    return result

def server_group_filter_v2(d,l,i,iface='ansible_eth1'):
    result = []
    if len(l) > 0:
        for item in l:
            if item != i:
                try:
                    ip_addr = d[item][iface]['ipv4']['address']
                    if ip_addr:
                        result.append(ip_addr)
                except:
                    pass
    return result

def server_group_ip_map(d,l):
    result = []
    if len(l) > 0:
        for item in l:
            try:
                ip_addr = d[item]['ansible_eth1']['ipv4']['address']
                if ip_addr:
                    result.append(ip_addr)
            except:
                pass
    return result

def server_group_ip_map_v2(d,l,iface='ansible_eth1'):
    result = []
    if len(l) > 0:
        for item in l:
            try:
                ip_addr = d[item][iface]['ipv4']['address']
                if ip_addr:
                    result.append(ip_addr)
            except:
                pass
    return result

def init_list(name):
    newlist = []
    newlist.append(name)
    return newlist

def convert_to_ip(name):
    ip_addr = hostvars['ansible_eth2']['ipv4']['address']
    if ip_addr:
        return ip_addr

class FilterModule(object):
    ''' utility filters for operating on hashes '''

    def filters(self):
        return {
            'hash_to_tuples' : hash_to_tuples
            ,'hash_keys'     : hash_keys
            ,'hash_values'   : hash_values
            ,'zipped_hash'   : zipped_hash
            ,'server_group_filter'  : server_group_filter
            ,'server_group_ip_map'  : server_group_ip_map
            ,'server_group_filter_v2'  : server_group_filter_v2
            ,'server_group_ip_map_v2'  : server_group_ip_map_v2
            ,'init_list'     : init_list
        }