import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

PSGC_BASE_URL = "https://psgc.rootscratch.com"

@require_GET
def get_regions(request):
    try:
        region_id = request.GET.get('region_id')
        params = {"id": region_id} if region_id else {}
        response = requests.get(f"{PSGC_BASE_URL}/region", params=params)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch regions"}, status=500)

@require_GET
def get_provinces(request):
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({"error": "region_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/province", params={"id": region_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch provinces"}, status=500)

@require_GET
def get_cities(request):
    province_id = request.GET.get('province_id')
    region_id = request.GET.get('region_id')
    try:
        if province_id:
            response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params={"id": province_id})
            response.raise_for_status()
            data = response.json()
            return JsonResponse(data, safe=False)
        elif region_id:
            # Fetch provinces for the region
            prov_response = requests.get(f"{PSGC_BASE_URL}/province", params={"id": region_id})
            prov_response.raise_for_status()
            provinces = prov_response.json()
            if provinces is None or len(provinces) == 0:
                # Fallback: fetch all cities and filter by region code
                response = requests.get(f"{PSGC_BASE_URL}/municipal-city")
                response.raise_for_status()
                data = response.json()
                filtered_cities = [city for city in data if city.get('regCode') == region_id or city.get('region_code') == region_id]
                return JsonResponse(filtered_cities, safe=False)
            all_cities = []
            for prov in provinces:
                city_response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params={"id": prov.get('psgc_id') or prov.get('code')})
                city_response.raise_for_status()
                cities = city_response.json()
                all_cities.extend(cities)
            return JsonResponse(all_cities, safe=False)
        else:
            return JsonResponse({"error": "province_id or region_id parameter is required"}, status=400)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch cities"}, status=500)

@require_GET
def get_barangays(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse({"error": "city_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/barangay", params={"id": city_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch barangays"}, status=500)

# Utility functions for backend name resolution

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

@require_GET
def get_provinces(request):
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({"error": "region_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/province", params={"id": region_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch provinces"}, status=500)

@require_GET
def get_cities(request):
    province_id = request.GET.get('province_id')
    region_id = request.GET.get('region_id')
    try:
        if province_id:
            response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params={"id": province_id})
            response.raise_for_status()
            data = response.json()
            return JsonResponse(data, safe=False)
        elif region_id:
            # Fetch provinces for the region
            prov_response = requests.get(f"{PSGC_BASE_URL}/province", params={"id": region_id})
            prov_response.raise_for_status()
            provinces = prov_response.json()
            if provinces is None or len(provinces) == 0:
                # Fallback: fetch all cities and filter by region code
                response = requests.get(f"{PSGC_BASE_URL}/municipal-city")
                response.raise_for_status()
                data = response.json()
                filtered_cities = [city for city in data if city.get('regCode') == region_id or city.get('region_code') == region_id]
                return JsonResponse(filtered_cities, safe=False)
            all_cities = []
            for prov in provinces:
                city_response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params={"id": prov.get('psgc_id') or prov.get('code')})
                city_response.raise_for_status()
                cities = city_response.json()
                all_cities.extend(cities)
            return JsonResponse(all_cities, safe=False)
        else:
            return JsonResponse({"error": "province_id or region_id parameter is required"}, status=400)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch cities"}, status=500)

@require_GET
def get_barangays(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse({"error": "city_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/barangay", params={"id": city_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch barangays"}, status=500)

# Utility functions for backend name resolution

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

