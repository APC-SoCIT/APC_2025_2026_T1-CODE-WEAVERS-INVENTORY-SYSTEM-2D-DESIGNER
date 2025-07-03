import requests

PSGC_BASE_URL = "https://psgc.rootscratch.com"

def get_region_name(region_id):
    try:
        params = {"id": region_id} if region_id else {}
        response = requests.get(f"{PSGC_BASE_URL}/region", params=params)
        response.raise_for_status()
        regions = response.json()
        for region in regions:
            if region.get('psgc_code') == region_id or region.get('code') == region_id:
                return region.get('name', region_id)
        return region_id
    except Exception:
        return region_id

def get_province_name(province_id):
    try:
        params = {"id": province_id} if province_id else {}
        response = requests.get(f"{PSGC_BASE_URL}/province", params=params)
        response.raise_for_status()
        provinces = response.json()
        for province in provinces:
            if province.get('psgc_id') == province_id or province.get('code') == province_id:
                return province.get('name', province_id)
        return province_id
    except Exception:
        return province_id

def get_citymun_name(citymun_id):
    try:
        params = {"id": citymun_id} if citymun_id else {}
        response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params=params)
        response.raise_for_status()
        cities = response.json()
        for city in cities:
            if city.get('psgc_id') == citymun_id or city.get('code') == citymun_id:
                return city.get('name', citymun_id)
        return citymun_id
    except Exception:
        return citymun_id

def get_barangay_name(barangay_id):
    try:
        params = {"id": barangay_id} if barangay_id else {}
        response = requests.get(f"{PSGC_BASE_URL}/barangay", params=params)
        response.raise_for_status()
        barangays = response.json()
        for barangay in barangays:
            if barangay.get('psgc_id') == barangay_id or barangay.get('code') == barangay_id:
                return barangay.get('name', barangay_id)
        return barangay_id
    except Exception:
        return barangay_id
