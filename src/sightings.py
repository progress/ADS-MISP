import traceback
import inputs
import flowmon_filters
import misp
from pymisp import ExpandedPyMISP as PyMISP

CACHE_FILE = "/tmp/flowmon_filters.json"
DEBUG_FILE = "/tmp/misp.exception"

try:
    options, ads_event = inputs.load_input_data()
    
    misp = PyMISP(options["misp_server"], options["misp_api_key"], False, debug=False)
    
    if "MISP" in ads_event["description"]:  
        for ip_key in ["source", "target"]:
            ip_values = ads_event[ip_key].split(",")
            for ip_value in ip_values:
                ip_value = ip_value.strip()
                for type_attribute in ["ip-src", "ip-dst"]:
                    attributes = misp.search(controller='attributes', type_attribute=type_attribute, value=ip_value, pythonify=True)
                    for attribute in attributes:
                        sighting = attribute.add_sighting({"source": options["source"]})
                        misp.add_sighting(sighting, attribute)


except Exception as e:
    with open(DEBUG_FILE, "a") as file:
        file.write(str(e))
        file.write(traceback.format_exc())
        file.write("\n")
