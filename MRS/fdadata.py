import requests

def get_fda_drug_labels(api_key, drug_name):
    base_url = "https://api.fda.gov/drug/label.json"
    
    params = {
        "search": f"brand_name:{drug_name}",
        "api_key": api_key
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
