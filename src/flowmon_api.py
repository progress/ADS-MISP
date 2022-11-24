import urllib3
import json
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_ads_filters(username, password, filters_names):
    body = {
        "grant_type": "password",
        "client_id": "invea-tech",
        "username": username,
        "password": password
    }
    api_url = "https://127.0.0.1"
    response = requests.post(api_url + "/resources/oauth/token", data=body, verify=False)
    responsejson = json.loads(response.text)
    token = responsejson["access_token"]
    bearer = {
        'Authorization': 'bearer ' + token,
    }
    filters = requests.get(api_url + '/rest/ads/filters', headers=bearer, verify=False)
    json_filter = json.loads(filters.text)

    result = []
    filters_names = filters_names.split(",")
    filters_names = [filters_name.strip() for filters_name in filters_names]
    for json_element in json_filter:
        filter_name = json_element['name'].strip()
        if filter_name not in filters_names:
            continue
        for pattern_obj in json_element['patterns']:
            result.append(pattern_obj['pattern'])
    return result
