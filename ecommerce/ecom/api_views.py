import requests
import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

PSGC_BASE_URL = "https://psgc.gitlab.io/api"

@require_GET
def get_regions(request):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/regions/")
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
        response = requests.get(f"{PSGC_BASE_URL}/regions/{region_id}/provinces/")
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
            response = requests.get(f"{PSGC_BASE_URL}/provinces/{province_id}/cities-municipalities/")
            response.raise_for_status()
            data = response.json()
            return JsonResponse(data, safe=False)
        elif region_id:
            # For NCR and similar regions without provinces
            response = requests.get(f"{PSGC_BASE_URL}/regions/{region_id}/cities-municipalities/")
            response.raise_for_status()
            data = response.json()
            return JsonResponse(data, safe=False)
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
        response = requests.get(f"{PSGC_BASE_URL}/cities-municipalities/{city_id}/barangays/")
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data, safe=False)
    except requests.RequestException:
        return JsonResponse({"error": "Failed to fetch barangays"}, status=500)

# Utility functions for backend name resolution
def get_region_name(region_id):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/regions/{region_id}/")
        response.raise_for_status()
        region = response.json()
        return region.get('name', region_id)
    except Exception:
        return region_id

def get_province_name(province_id):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/provinces/{province_id}/")
        response.raise_for_status()
        province = response.json()
        return province.get('name', province_id)
    except Exception:
        return province_id

def get_citymun_name(citymun_id):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/cities-municipalities/{citymun_id}/")
        response.raise_for_status()
        city = response.json()
        return city.get('name', citymun_id)
    except Exception:
        return citymun_id

def get_barangay_name(barangay_id):
    try:
        response = requests.get(f"{PSGC_BASE_URL}/barangays/{barangay_id}/")
        response.raise_for_status()
        barangay = response.json()
        return barangay.get('name', barangay_id)
    except Exception:
        return barangay_id

@csrf_exempt
@require_POST
def generate_ai_design(request):
    """
    Generate AI-powered jersey design based on user prompt
    """
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return JsonResponse({'error': 'Prompt is required'}, status=400)
        
        # For now, we'll use a sophisticated rule-based AI system
        # In production, you could integrate with OpenAI API
        design = generate_intelligent_design(prompt)
        
        return JsonResponse({
            'success': True,
            'design': design,
            'message': 'AI design generated successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generate_intelligent_design(prompt):
    """
    Advanced AI design generation logic
    """
    prompt_lower = prompt.lower()
    words = prompt_lower.split()
    
    # AI Knowledge Base
    ai_knowledge = {
        'themes': {
            'fire': {'colors': ['#ff4500', '#ff0000', '#ffd700'], 'patterns': ['flame', 'wave'], 'intensity': 'high'},
            'ocean': {'colors': ['#0066cc', '#00bfff', '#ffffff'], 'patterns': ['wave', 'flow'], 'intensity': 'medium'},
            'forest': {'colors': ['#228b22', '#32cd32', '#8fbc8f'], 'patterns': ['leaf', 'organic'], 'intensity': 'low'},
            'lightning': {'colors': ['#ffff00', '#9370db', '#000000'], 'patterns': ['lightning', 'electric'], 'intensity': 'high'},
            'sunset': {'colors': ['#ff6347', '#ffa500', '#ff69b4'], 'patterns': ['gradient', 'soft'], 'intensity': 'medium'},
            'galaxy': {'colors': ['#4b0082', '#8a2be2', '#00ced1'], 'patterns': ['star', 'cosmic'], 'intensity': 'high'},
            'arctic': {'colors': ['#87ceeb', '#ffffff', '#b0e0e6'], 'patterns': ['ice', 'crystal'], 'intensity': 'low'},
            'desert': {'colors': ['#daa520', '#cd853f', '#f4a460'], 'patterns': ['sand', 'dune'], 'intensity': 'medium'}
        },
        'emotions': {
            'aggressive': {'colors': ['#ff0000', '#000000', '#ff4500'], 'intensity': 'high'},
            'calm': {'colors': ['#87ceeb', '#98fb98', '#f0f8ff'], 'intensity': 'low'},
            'energetic': {'colors': ['#ff1493', '#00ff00', '#ffff00'], 'intensity': 'high'},
            'professional': {'colors': ['#000080', '#ffffff', '#c0c0c0'], 'intensity': 'medium'},
            'elegant': {'colors': ['#4b0082', '#ffd700', '#ffffff'], 'intensity': 'low'},
            'bold': {'colors': ['#ff0000', '#ffff00', '#000000'], 'intensity': 'high'}
        },
        'sports': {
            'soccer': {'patterns': ['hexagon', 'net'], 'logos': ['ball', 'goal'], 'colors': ['#00ff00', '#ffffff']},
            'basketball': {'patterns': ['court', 'lines'], 'logos': ['ball', 'hoop'], 'colors': ['#ff8c00', '#000000']},
            'football': {'patterns': ['field', 'yard'], 'logos': ['helmet', 'field'], 'colors': ['#8b4513', '#ffffff']},
            'baseball': {'patterns': ['diamond', 'stitch'], 'logos': ['bat', 'ball'], 'colors': ['#ffffff', '#ff0000']}
        }
    }
    
    design = {
        'colors': [],
        'gradient': False,
        'gradientDirection': 'to right',
        'patterns': [],
        'logoPosition': 'center',
        'logoType': 'intelligent',
        'theme': None,
        'emotion': None,
        'sport': None,
        'complexity': 'medium',
        'textElements': []
    }
    
    # Detect themes
    for theme, data in ai_knowledge['themes'].items():
        if theme in prompt_lower or any(word in prompt_lower for word in [theme]):
            design['theme'] = theme
            design['colors'].extend(data['colors'][:2])
            design['patterns'].extend(data['patterns'][:1])
            break
    
    # Detect emotions
    for emotion, data in ai_knowledge['emotions'].items():
        if emotion in prompt_lower:
            design['emotion'] = emotion
            if not design['colors']:
                design['colors'].extend(data['colors'][:2])
            break
    
    # Detect sports
    for sport, data in ai_knowledge['sports'].items():
        if sport in prompt_lower:
            design['sport'] = sport
            design['patterns'].extend(data['patterns'][:1])
            if not design['colors']:
                design['colors'].extend(data['colors'])
            break
    
    # Enhanced color detection with better parsing
    color_map = {
        'red': '#ff0000', 'crimson': '#dc143c', 'scarlet': '#ff2400', 'cherry': '#de3163',
        'blue': '#0066cc', 'navy': '#000080', 'royal': '#4169e1', 'sky': '#87ceeb', 'azure': '#007fff',
        'green': '#00ff00', 'forest': '#228b22', 'lime': '#32cd32', 'emerald': '#50c878', 'mint': '#98fb98',
        'yellow': '#ffff00', 'gold': '#ffd700', 'amber': '#ffbf00', 'lemon': '#fff700',
        'orange': '#ffa500', 'tangerine': '#ff8c00', 'coral': '#ff7f50', 'peach': '#ffcba4',
        'purple': '#800080', 'violet': '#ee82ee', 'indigo': '#4b0082', 'lavender': '#e6e6fa',
        'pink': '#ffc0cb', 'rose': '#ff007f', 'fuchsia': '#ff00ff', 'magenta': '#ff00ff',
        'black': '#000000', 'white': '#ffffff', 'gray': '#808080', 'grey': '#808080',
        'silver': '#c0c0c0', 'brown': '#a52a2a', 'cyan': '#00ffff', 'turquoise': '#40e0d0'
    }
    
    # Parse colors in order they appear in the prompt
    detected_colors = []
    prompt_words = prompt_lower.split()
    
    for i, word in enumerate(prompt_words):
        # Check for color names
        for color_name, hex_code in color_map.items():
            if word == color_name or (len(word) > 3 and color_name in word):
                if hex_code not in detected_colors:
                    detected_colors.append(hex_code)
                break
    
    # If colors were detected, use them in order
    if detected_colors:
        design['colors'] = detected_colors
    
    # Enhanced gradient detection
    gradient_keywords = ['gradient', 'gradiant', 'fade', 'blend', 'transition', 'ombre']
    has_gradient_keyword = any(keyword in prompt_lower for keyword in gradient_keywords)
    has_multiple_colors = len(detected_colors) >= 2
    
    # Detect gradient if keyword is present OR multiple colors are mentioned
    if has_gradient_keyword or (has_multiple_colors and any(word in prompt_lower for word in ['and', 'to', 'with'])):
        design['gradient'] = True
        if 'vertical' in prompt_lower or 'up' in prompt_lower or 'down' in prompt_lower:
            design['gradientDirection'] = 'to bottom'
        elif 'diagonal' in prompt_lower or 'corner' in prompt_lower:
            design['gradientDirection'] = 'to bottom right'
        elif 'radial' in prompt_lower or 'circular' in prompt_lower or 'center' in prompt_lower:
            design['gradientDirection'] = 'circle at center'
        else:
            design['gradientDirection'] = 'to right'
    
    # Pattern detection
    pattern_keywords = {
        'stripes': 'stripes', 'lines': 'stripes', 'geometric': 'geometric',
        'circles': 'circles', 'dots': 'dots', 'waves': 'wave',
        'flames': 'flame', 'fire': 'flame', 'lightning': 'lightning',
        'stars': 'star', 'leaves': 'leaf', 'tribal': 'tribal'
    }
    
    for keyword, pattern in pattern_keywords.items():
        if keyword in prompt_lower and pattern not in design['patterns']:
            design['patterns'].append(pattern)
    
    # Logo position detection
    if 'left' in prompt_lower:
        design['logoPosition'] = 'left'
    elif 'right' in prompt_lower:
        design['logoPosition'] = 'right'
    elif 'top' in prompt_lower:
        design['logoPosition'] = 'top'
    elif 'bottom' in prompt_lower:
        design['logoPosition'] = 'bottom'
    
    # Text elements detection
    text_keywords = ['text', 'name', 'number', 'title', 'slogan']
    if any(keyword in prompt_lower for keyword in text_keywords):
        design['textElements'].append({
            'type': 'custom',
            'content': 'AI Generated',
            'position': 'center'
        })
    
    # Default colors if none detected
    if not design['colors']:
        design['colors'] = ['#0066cc', '#ffffff']
    
    # Ensure we have at least 2 colors for gradients
    if design['gradient'] and len(design['colors']) < 2:
        design['colors'].append('#ffffff')
    
    # Default pattern if none detected
    if not design['patterns']:
        design['patterns'] = ['modern']
    
    return design

