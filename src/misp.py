import ipaddress
import urllib3
from pymisp import ExpandedPyMISP as PyMISP
from pymisp import MISPEvent, MISPAttribute

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_attributes_from_ads_event(ads_event):
    attributes = []
    attributes.append({"type": "ip-src", "value": ads_event["source"]})
    targets = ads_event["target"].split(",")
    for ip in targets:
        ip = ip.strip()
        if ip != '':
            attributes.append({"type": "ip-dst", "value": ip})
    return attributes


def filter_match_ip(ip, ip_filters):
    for ip_filter in ip_filters:
        if ip in ip_filter:
            return True
    return False


def filter_out_invalid_attributes(attributes, ip_filters):
    valid_attributes = []
    for attribute in attributes:
        try:
            ip_address = ipaddress.ip_address(attribute["value"])
            if not filter_match_ip(ip_address, ip_filters):
                valid_attributes.append(attribute)
        except:
            pass
    return valid_attributes


def create_misp_attribute(attribute, ids, distribution):
    misp_attribute = MISPAttribute()
    misp_attribute.type = attribute["type"]
    misp_attribute.value = attribute["value"]
    misp_attribute.category = "Network activity"
    misp_attribute.to_ids = bool(ids)
    misp_attribute.distribution = distribution
    return misp_attribute


def encode_severity(value):
    codes = {"Informational": 3, "Low": 3, "Medium": 2, "High": 1, "Critical": 1}
    return codes[value]


def create_event(misp_server, misp_api_key, misp_tag, misp_ids, misp_distribution, ads_event, ip_filters):
    attributes = extract_attributes_from_ads_event(ads_event)
    attributes = filter_out_invalid_attributes(attributes, ip_filters)

    if len(attributes) == 0:
        return

    misp_instance = PyMISP(misp_server, misp_api_key, False)
    misp_event = MISPEvent()
    misp_event.distribution = misp_distribution
    misp_event.info = ads_event["event_type_long"] + ": " + ads_event["description"]
    misp_event.threat_level_id = encode_severity(ads_event["severity"])
    misp_event.analysis = 0

    try:
        existing_tags = misp_instance.search_tags(misp_tag)
        if len(existing_tags) != 0:
            misp_event.add_tag(existing_tags[0])
        else:
            misp_event.add_tag(misp_tag)
            misp_instance.add_tag(misp_event.tags[0], pythonify=True)
            
        misp_event.add_tag(ads_event["event_type"])
        misp_instance.add_tag(misp_event.tags[-1])
    except:  # crashes with older PyMISP versions
        pass
    
    misp_instance.add_event(misp_event, pythonify=True)
    for attribute in attributes:
        misp_instance.add_attribute(misp_event, create_misp_attribute(attribute, misp_ids, misp_distribution))
    misp_instance.publish(misp_event)

