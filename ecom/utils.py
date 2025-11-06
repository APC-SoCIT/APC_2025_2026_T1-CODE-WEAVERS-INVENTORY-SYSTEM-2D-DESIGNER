import requests
import json
import os
from django.core.cache import cache
from django.conf import settings

# Prefer LOCAL data lookups and in-process caches for speed.
# Only hit external PSGC API if explicitly enabled via settings.
PSGC_USE_API = getattr(settings, 'PSGC_USE_API', False)

# Module-level maps for O(1) lookups without repeated file reads
_REGION_MAP = {}
_PROVINCE_MAP = {}
_CITYMUN_MAP = {}
_BARANGAY_MAP = {}

# Map Django-style region codes to PSGC numeric codes for external lookups
DJANGO_TO_PSGC_REGION = {
    'R1': '010000000',
    'R2': '020000000',
    'R3': '030000000',
    'R4A': '040000000',
    'R4B': '170000000',
    'R5': '050000000',
    'R6': '060000000',
    'R7': '070000000',
    'R8': '080000000',
    'R9': '090000000',
    'R10': '100000000',
    'R11': '110000000',
    'R12': '120000000',
    'NCR': '130000000',
    'CAR': '140000000',
    'R13': '160000000',
    'BARMM': '150000000',
}

def _normalize_region_code(region_code: str) -> str:
    if not region_code:
        return region_code
    if str(region_code).isdigit():
        return str(region_code)
    return DJANGO_TO_PSGC_REGION.get(str(region_code), str(region_code))

def _init_local_maps():
    """Initialize local PSGC maps once per process."""
    global _REGION_MAP, _PROVINCE_MAP, _CITYMUN_MAP, _BARANGAY_MAP
    try:
        data = load_local_psgc_data()

        # Regions: support different file structures
        _REGION_MAP = {}
        regions_src = data.get('regions')
        if isinstance(regions_src, dict):
            regions_src = regions_src.get('region') or regions_src.get('regions') or []
        if not isinstance(regions_src, list):
            regions_src = []
        for r in regions_src:
            if not isinstance(r, dict):
                continue
            key = str(
                r.get('regCode') or r.get('psgcCode') or r.get('code') or ''
            ).strip()
            val = (
                r.get('regDesc') or r.get('name') or r.get('desc') or ''
            )
            if key:
                _REGION_MAP[key] = val

        # Provinces
        _PROVINCE_MAP = {}
        provinces_src = data.get('provinces')
        if isinstance(provinces_src, dict):
            provinces_src = provinces_src.get('province') or provinces_src.get('provinces') or []
        if not isinstance(provinces_src, list):
            provinces_src = []
        for p in provinces_src:
            if not isinstance(p, dict):
                continue
            key = str(p.get('provCode') or p.get('code') or '').strip()
            val = p.get('provDesc') or p.get('name') or ''
            if key:
                _PROVINCE_MAP[key] = val

        # City/Municipalities
        _CITYMUN_MAP = {}
        citymun_src = data.get('citymun')
        if isinstance(citymun_src, dict):
            citymun_src = citymun_src.get('citymun') or citymun_src.get('cities') or []
        if not isinstance(citymun_src, list):
            citymun_src = []
        for c in citymun_src:
            if not isinstance(c, dict):
                continue
            key = str(c.get('citymunCode') or c.get('code') or '').strip()
            val = c.get('citymunDesc') or c.get('name') or ''
            if key:
                _CITYMUN_MAP[key] = val

        # Barangays
        _BARANGAY_MAP = {}
        barangay_src = data.get('barangays')
        if isinstance(barangay_src, dict):
            barangay_src = barangay_src.get('barangay') or barangay_src.get('barangays') or []
        if not isinstance(barangay_src, list):
            barangay_src = []
        for b in barangay_src:
            if not isinstance(b, dict):
                continue
            key = str(b.get('brgyCode') or b.get('code') or '').strip()
            val = b.get('brgyDesc') or b.get('name') or ''
            if key:
                _BARANGAY_MAP[key] = val
    except Exception as e:
        # Keep maps empty if any error; functions will fallback to generic labels
        print(f"Error initializing PSGC maps: {e}")

# Defer initializing maps until after load_local_psgc_data is defined

def load_local_psgc_data():
    """Load local PSGC data as fallback"""
    try:
        static_dir = getattr(settings, 'STATIC_ROOT', None) or os.path.join(settings.BASE_DIR, 'staticfiles')
        
        # Load regions
        regions_file = os.path.join(static_dir, 'ecom', 'refregion.json')
        if os.path.exists(regions_file):
            with open(regions_file, 'r', encoding='utf-8') as f:
                regions_data = json.load(f)
        else:
            regions_data = []
            
        # Load provinces
        provinces_file = os.path.join(static_dir, 'ecom', 'refprovince.json')
        if os.path.exists(provinces_file):
            with open(provinces_file, 'r', encoding='utf-8') as f:
                provinces_data = json.load(f)
        else:
            provinces_data = []
            
        # Load cities/municipalities
        citymun_file = os.path.join(static_dir, 'ecom', 'refcitymun.json')
        if os.path.exists(citymun_file):
            with open(citymun_file, 'r', encoding='utf-8') as f:
                citymun_data = json.load(f)
        else:
            citymun_data = []
            
        # Load barangays
        barangay_file = os.path.join(static_dir, 'ecom', 'refbrgy.json')
        if os.path.exists(barangay_file):
            with open(barangay_file, 'r', encoding='utf-8') as f:
                barangay_data = json.load(f)
        else:
            barangay_data = []
            
        return {
            'regions': regions_data,
            'provinces': provinces_data,
            'citymun': citymun_data,
            'barangays': barangay_data
        }
    except Exception as e:
        print(f"Error loading local PSGC data: {e}")
        return {
            'regions': [],
            'provinces': [],
            'citymun': [],
            'barangays': []
        }

# Initialize maps now that load_local_psgc_data is available
_init_local_maps()

def get_region_name(region_code):
    """Get region name; prefer local map, then fetch from PSGC API."""
    if not region_code:
        return "Unknown Region"
        
    # Check cache first
    cache_key = f"region_{region_code}"
    cached_name = cache.get(cache_key)
    if cached_name:
        return cached_name
    # Prefer local map first (fast, in-process)
    key = str(region_code)
    name = _REGION_MAP.get(key)
    if name:
        cache.set(cache_key, name, 3600)
        return name

    # Attempt API fetch as a fallback
    try:
        base_url = getattr(settings, 'PSGC_API_BASE_URL', 'https://psgc.gitlab.io/api')
        norm_code = _normalize_region_code(region_code)
        url = f"{base_url}/regions/{norm_code}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        name = None
        if isinstance(data, dict) and 'name' in data:
            name = data['name']
        elif isinstance(data, list) and len(data) > 0 and 'name' in data[0]:
            name = data[0]['name']
        if name:
            cache.set(cache_key, name, 3600)  # Cache for 1 hour
            return name
    except Exception as e:
        print(f"API error for region {region_code}: {e}")

    # Fallback: return code as-is without category label
    return str(region_code)

def get_province_name(province_code):
    """Get province name; prefer local map, then fetch from PSGC API."""
    if not province_code:
        return "Unknown Province"
        
    # Check cache first
    cache_key = f"province_{province_code}"
    cached_name = cache.get(cache_key)
    if cached_name:
        return cached_name
    # Prefer local map first
    key = str(province_code)
    name = _PROVINCE_MAP.get(key)
    if name:
        cache.set(cache_key, name, 3600)
        return name

    # Attempt API fetch as a fallback
    try:
        base_url = getattr(settings, 'PSGC_API_BASE_URL', 'https://psgc.gitlab.io/api')
        url = f"{base_url}/provinces/{province_code}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        name = None
        if isinstance(data, dict) and 'name' in data:
            name = data['name']
        elif isinstance(data, list) and len(data) > 0 and 'name' in data[0]:
            name = data[0]['name']
        if name:
            cache.set(cache_key, name, 3600)
            return name
    except Exception as e:
        print(f"API error for province {province_code}: {e}")

    # Fallback: return code as-is without category label
    return str(province_code)

def get_citymun_name(citymun_code):
    """Get city/municipality name; prefer local map, then fetch from PSGC API."""
    if not citymun_code:
        return "Unknown City/Municipality"
        
    # Check cache first
    cache_key = f"citymun_{citymun_code}"
    cached_name = cache.get(cache_key)
    if cached_name:
        return cached_name
    # Prefer local map first
    key = str(citymun_code)
    name = _CITYMUN_MAP.get(key)
    if name:
        cache.set(cache_key, name, 3600)
        return name

    # Attempt API fetch as a fallback
    try:
        base_url = getattr(settings, 'PSGC_API_BASE_URL', 'https://psgc.gitlab.io/api')
        url = f"{base_url}/cities-municipalities/{citymun_code}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        name = None
        if isinstance(data, dict) and 'name' in data:
            name = data['name']
        elif isinstance(data, list) and len(data) > 0 and 'name' in data[0]:
            name = data[0]['name']
        if name:
            cache.set(cache_key, name, 3600)
            return name
    except Exception as e:
        print(f"API error for citymun {citymun_code}: {e}")

    # Fallback: return code as-is without category label
    return str(citymun_code)

def get_barangay_name(barangay_code):
    """Get barangay name; prefer local map, then fetch from PSGC API."""
    if not barangay_code:
        return "Unknown Barangay"
        
    # Check cache first
    cache_key = f"barangay_{barangay_code}"
    cached_name = cache.get(cache_key)
    if cached_name:
        return cached_name
    # Prefer local map first
    key = str(barangay_code)
    name = _BARANGAY_MAP.get(key)
    if name:
        cache.set(cache_key, name, 3600)
        return name

    # Attempt API fetch as a fallback
    try:
        base_url = getattr(settings, 'PSGC_API_BASE_URL', 'https://psgc.gitlab.io/api')
        url = f"{base_url}/barangays/{barangay_code}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        name = None
        if isinstance(data, dict) and 'name' in data:
            name = data['name']
        elif isinstance(data, list) and len(data) > 0 and 'name' in data[0]:
            name = data[0]['name']
        if name:
            cache.set(cache_key, name, 3600)
            return name
    except Exception as e:
        print(f"API error for barangay {barangay_code}: {e}")

    # Fallback: return code as-is without category label
    return str(barangay_code)
