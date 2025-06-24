import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

PSGC_BASE_URL = "https://psgc.rootscratch.com"

@require_GET
def get_regions(request):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/region")
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

