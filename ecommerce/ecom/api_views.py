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
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch regions"}, status=500)

@require_GET
def get_provinces(request):
    region_id = request.GET.get('region_id')
    if not region_id:
        return JsonResponse({"error": "region_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/region", params={"id": region_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch provinces"}, status=500)

@require_GET
def get_cities(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse({"error": "province_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/province", params={"id": province_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch cities"}, status=500)

@require_GET
def get_barangays(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse({"error": "city_id parameter is required"}, status=400)
    try:
        response = requests.get(f"{PSGC_BASE_URL}/municipal-city", params={"id": city_id})
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to fetch barangays"}, status=500)
