import traceback
import inputs
import flowmon_filters
import misp

CACHE_FILE = "/tmp/flowmon_filters.json"
DEBUG_FILE = "/tmp/misp.exception"

try:
    options, ads_event = inputs.load_input_data()
    ip_filters = flowmon_filters.get_ip_filters(CACHE_FILE, options["flowmon_user"], options["flowmon_pass"], options["flowmon_filters"])
    misp.create_event(options["misp_server"], options["misp_api_key"], options["misp_tag"], options["misp_ids"], options["misp_distribution"], ads_event, ip_filters)
except Exception as e:
    with open(DEBUG_FILE, "a") as file:
        file.write(str(e))
        file.write(traceback.format_exc())
        file.write("\n")
