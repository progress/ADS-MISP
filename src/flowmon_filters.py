import ipaddress
import json
import re
import time
import flowmon_api

DEFAULT_FILTERS = ["0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12", "192.168.0.0/16", "192.0.0.8/32", "192.0.0.9/32", "192.0.0.10/32", "192.0.0.170/32", "192.0.0.171/32", "192.0.2.0/24", "192.31.196.0/24", "192.52.193.0/24", "192.88.99.0/24", "192.168.0.0/16", "192.175.48.0/24", "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24", "224.0.0.0/3", "::1/128", "::/128", "::ffff:0:0/96", "64:ff9b::/96", "64:ff9b:1::/48", "100::/64", "2001::/23", "2001::/32", "2001:1::1/128", "2001:1::2/128", "2001:2::/48", "2001:3::/32", "2001:4:112::/48", "2001:10::/28", "2001:20::/28", "2001:db8::/32", "2002::/16", "2620:4f:8000::/48", "fc00::/7", "fe80::/10"]
CACHE_VALIDITY = 300


def parse_range(str_ip):
    to_replace = re.search(r"\[(\d*)-(\d*)]", str_ip).group(0)
    begin = re.search(r"\[(\d*)-(\d*)]", str_ip).group(1)
    end = re.search(r"\[(\d*)-(\d*)]", str_ip).group(2)
    ip_list = []
    for i in range(int(begin), int(end) + 1):
        tmp = str_ip.replace(to_replace, str(i))
        ip_list.append(ipaddress.ip_address(tmp))
    return ip_list


def parse_ip_range(str_ip):
    preparsed = str_ip.split("-")
    start_ip = ipaddress.ip_address(preparsed[0].strip())
    end_ip = ipaddress.ip_address(preparsed[1].strip())
    return [ipaddr for ipaddr in ipaddress.summarize_address_range(start_ip, end_ip)]


def parse_star(str_ip):
    ip_addresses = []
    for i in range(256):
        tmp = str_ip.replace("*", str(i))
        ip_addresses.append(ipaddress.ip_address(tmp))
    return ip_addresses


def parse_select(str_ip):
    to_replace = re.search(r"\{.*}", str_ip).group(0)
    values = to_replace[1:-1].split(",")
    ip_list = []
    for element in values:
        tmp = str_ip.replace(to_replace, element)
        ip_list.append(ipaddress.ip_address(tmp))
    return ip_list


def ipv6_parser(str_ip):
    if "-" in str_ip:
        return parse_ip_range(str_ip)
    return [ipaddress.ip_network(str_ip)]


def ipv4_parser(str_ip):
    ipv4_regex = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")
    if "[" in str_ip:
        return parse_range(str_ip)
    elif "-" in str_ip:
        return parse_ip_range(str_ip)
    elif "*" in str_ip:
        return parse_star(str_ip)
    elif "{" in str_ip:
        return parse_select(str_ip)
    elif ipv4_regex.match(str_ip):
        return ipaddress.ip_network(str_ip, False)


def parse_raw_filters(ip_filters):
    cidrs = []
    for str_ip in ip_filters:
        if ":" in str_ip:
            cidrs += ipv6_parser(str_ip)
        else:
            cidrs += ipv4_parser(str_ip)
    cidrs = list(filter(lambda x: x is not None, cidrs))
    return cidrs


def read_cache(cache_file_path):
    try:
        with open(cache_file_path, 'r') as f:
            data = json.load(f)
    except:
        data = None
    return data


def is_cache_valid(cache):
    if cache is None:
        return False
    if time.time() - int(cache["time"]) > CACHE_VALIDITY:
        return False
    return True


def write_ads_filters_to_cache_file(cache_file_path, ads_filters_raw):
    output = {"time": time.time(), "ads_filters_raw": ads_filters_raw}
    with open(cache_file_path, "w") as file:
        json.dump(output, file)


def update_cache(cache_file_path, username, password, filters_names):
    ads_filters_raw = flowmon_api.get_ads_filters(username, password, filters_names)
    write_ads_filters_to_cache_file(cache_file_path, ads_filters_raw)
    return


def get_default_filters():
    default_filters = list(map(lambda x: ipaddress.ip_network(x), DEFAULT_FILTERS))
    return default_filters


def get_ip_filters(cache_file_path, username, password, filters_names):
    cache = read_cache(cache_file_path)
    if not is_cache_valid(cache):
        update_cache(cache_file_path, username, password, filters_names)
        cache = read_cache(cache_file_path)
    ads_filters = parse_raw_filters(cache["ads_filters_raw"])
    ads_filters += get_default_filters()
    ads_filters = list(set(ads_filters))

    return ads_filters
