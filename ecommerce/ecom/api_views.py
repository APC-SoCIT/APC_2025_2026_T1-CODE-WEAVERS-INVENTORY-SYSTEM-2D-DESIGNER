import requests
import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect

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

@csrf_protect
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
    Advanced AI design generation logic with enhanced visual elements
    """
    prompt_lower = prompt.lower()
    words = prompt_lower.split()
    
    # Enhanced AI Knowledge Base
    ai_knowledge = {
        'themes': {
            'fire': {
                'colors': ['#ff4500', '#ff0000', '#ffd700', '#ff6347'], 
                'patterns': ['flame', 'wave', 'radial', 'lightning'], 
                'shapes': ['triangle', 'diamond', 'flame-shape'],
                'textures': ['rough', 'glowing', 'ember'],
                'effects': ['glow', 'flicker', 'heat-wave'],
                'intensity': 'high'
            },
            'ocean': {
                'colors': ['#0066cc', '#00bfff', '#ffffff', '#20b2aa'], 
                'patterns': ['wave', 'flow', 'ripple', 'organic'], 
                'shapes': ['circle', 'oval', 'wave-form'],
                'textures': ['smooth', 'flowing', 'liquid'],
                'effects': ['shimmer', 'reflection', 'depth'],
                'intensity': 'medium'
            },
            'forest': {
                'colors': ['#228b22', '#32cd32', '#8fbc8f', '#006400'], 
                'patterns': ['leaf', 'organic', 'branch', 'hexagonal'], 
                'shapes': ['hexagon', 'leaf-shape', 'tree'],
                'textures': ['natural', 'bark', 'moss'],
                'effects': ['shadow', 'dappled-light', 'growth'],
                'intensity': 'low'
            },
            'tech': {
                'colors': ['#00ffff', '#0080ff', '#ffffff', '#c0c0c0'], 
                'patterns': ['tech', 'circuit', 'geometric', 'mesh'], 
                'shapes': ['square', 'rectangle', 'hexagon'],
                'textures': ['metallic', 'digital', 'grid'],
                'effects': ['neon-glow', 'digital-pulse', 'scan-lines'],
                'intensity': 'high'
            },
            'futuristic': {
                'colors': ['#00ffff', '#ff00ff', '#ffff00', '#000000'], 
                'patterns': ['circuit', 'tech', 'hexagonal', 'carbon'], 
                'shapes': ['hexagon', 'triangle', 'diamond'],
                'textures': ['metallic', 'holographic', 'carbon-fiber'],
                'effects': ['hologram', 'laser', 'energy-field'],
                'intensity': 'high'
            },
            'tribal': {
                'colors': ['#8b4513', '#d2691e', '#000000', '#ffffff'], 
                'patterns': ['tribal', 'organic', 'spiral'], 
                'shapes': ['triangle', 'diamond', 'spiral'],
                'textures': ['rough', 'earthy', 'carved'],
                'effects': ['shadow', 'depth', 'ancient'],
                'intensity': 'medium'
            },
            'carbon': {
                'colors': ['#2f2f2f', '#808080', '#000000', '#c0c0c0'], 
                'patterns': ['carbon', 'mesh', 'hexagonal'], 
                'shapes': ['hexagon', 'diamond', 'circle'],
                'textures': ['carbon-fiber', 'woven', 'metallic'],
                'effects': ['metallic-shine', 'depth', 'industrial'],
                'intensity': 'medium'
            },
            'lightning': {
                'colors': ['#ffff00', '#9370db', '#000000', '#ffffff'], 
                'patterns': ['lightning', 'electric', 'zigzag'], 
                'shapes': ['jagged', 'bolt', 'spark'],
                'textures': ['electric', 'sharp', 'crackling'],
                'effects': ['flash', 'electric-glow', 'spark'],
                'intensity': 'high'
            },
            'sunset': {
                'colors': ['#ff6347', '#ffa500', '#ff69b4', '#ff4500'], 
                'patterns': ['gradient', 'soft', 'horizon'], 
                'shapes': ['circle', 'semi-circle', 'cloud'],
                'textures': ['soft', 'warm', 'glowing'],
                'effects': ['warm-glow', 'fade', 'silhouette'],
                'intensity': 'medium'
            },
            'galaxy': {
                'colors': ['#4b0082', '#8a2be2', '#00ced1', '#ff1493'], 
                'patterns': ['star', 'cosmic', 'spiral'], 
                'shapes': ['star', 'spiral', 'nebula'],
                'textures': ['cosmic', 'starry', 'nebulous'],
                'effects': ['twinkle', 'cosmic-glow', 'depth'],
                'intensity': 'high'
            },
            'arctic': {
                'colors': ['#87ceeb', '#ffffff', '#b0e0e6', '#e0ffff'], 
                'patterns': ['ice', 'crystal', 'snowflake'], 
                'shapes': ['hexagon', 'crystal', 'snowflake'],
                'textures': ['icy', 'crystalline', 'frozen'],
                'effects': ['frost', 'ice-shine', 'crystal-refraction'],
                'intensity': 'low'
            },
            'desert': {
                'colors': ['#daa520', '#cd853f', '#f4a460', '#d2691e'], 
                'patterns': ['sand', 'dune', 'wave'], 
                'shapes': ['pyramid', 'dune', 'cactus'],
                'textures': ['sandy', 'rough', 'dry'],
                'effects': ['heat-shimmer', 'sand-drift', 'mirage'],
                'intensity': 'medium'
            },
            'tech': {
                'colors': ['#00ffff', '#0080ff', '#ffffff', '#c0c0c0'], 
                'patterns': ['circuit', 'grid', 'digital'], 
                'shapes': ['rectangle', 'square', 'hexagon'],
                'textures': ['metallic', 'digital', 'sleek'],
                'effects': ['neon-glow', 'scan-line', 'hologram'],
                'intensity': 'high'
            },
            'vintage': {
                'colors': ['#8b4513', '#daa520', '#cd853f', '#f5deb3'], 
                'patterns': ['vintage', 'ornate', 'classic'], 
                'shapes': ['ornament', 'frame', 'scroll'],
                'textures': ['aged', 'worn', 'classic'],
                'effects': ['sepia', 'aged', 'vintage-filter'],
                'intensity': 'medium'
            }
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
        'shapes': [],
        'textures': [],
        'effects': [],
        'visualElements': [],
        'logoPosition': 'center',
        'logoType': 'intelligent',
        'theme': None,
        'emotion': None,
        'sport': None,
        'complexity': 'medium',
        'textElements': [],
        'backgroundType': 'solid',
        'layering': 'simple',
        'composition': 'centered'
    }
    
    # Detect themes with enhanced visual elements
    for theme, data in ai_knowledge['themes'].items():
        if theme in prompt_lower or any(word in prompt_lower for word in [theme]):
            design['theme'] = theme
            design['colors'].extend(data['colors'][:3])  # More colors
            design['patterns'].extend(data['patterns'][:2])  # More patterns
            design['shapes'].extend(data.get('shapes', [])[:2])  # Add shapes
            design['textures'].extend(data.get('textures', [])[:2])  # Add textures
            design['effects'].extend(data.get('effects', [])[:2])  # Add effects
            
            # Set background type based on theme
            if theme in ['galaxy', 'ocean', 'sunset']:
                design['backgroundType'] = 'complex'
            elif theme in ['tech', 'lightning']:
                design['backgroundType'] = 'geometric'
            else:
                design['backgroundType'] = 'textured'
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
    
    # Enhanced pattern and shape detection
    pattern_keywords = {
        'stripes': 'stripes', 'lines': 'stripes', 'geometric': 'geometric',
        'circles': 'circles', 'dots': 'dots', 'waves': 'wave',
        'flames': 'flame', 'fire': 'flame', 'lightning': 'lightning',
        'stars': 'star', 'leaves': 'leaf', 'tribal': 'tribal',
        'grid': 'grid', 'mesh': 'mesh', 'honeycomb': 'honeycomb',
        'spiral': 'spiral', 'swirl': 'swirl', 'abstract': 'abstract',
        'hexagonal': 'hexagonal', 'hexagon': 'hexagonal', 'hex': 'hexagonal',
        'tech': 'tech', 'circuit': 'circuit', 'digital': 'tech',
        'organic': 'organic', 'natural': 'organic', 'flowing': 'organic',
        'diamond': 'diamond', 'diamonds': 'diamond', 'crystal': 'diamond',
        'carbon': 'carbon', 'fiber': 'carbon', 'weave': 'carbon'
    }
    
    shape_keywords = {
        'circle': 'circle', 'round': 'circle', 'sphere': 'circle',
        'square': 'square', 'rectangle': 'rectangle', 'box': 'rectangle',
        'triangle': 'triangle', 'arrow': 'triangle', 'diamond': 'diamond',
        'star': 'star', 'polygon': 'polygon', 'hexagon': 'hexagon',
        'heart': 'heart', 'cross': 'cross', 'plus': 'cross'
    }
    
    texture_keywords = {
        'smooth': 'smooth', 'rough': 'rough', 'metallic': 'metallic',
        'glossy': 'glossy', 'matte': 'matte', 'textured': 'textured',
        'fabric': 'fabric', 'leather': 'leather', 'wood': 'wood',
        'stone': 'stone', 'glass': 'glass', 'plastic': 'plastic'
    }
    
    effect_keywords = {
        'glow': 'glow', 'shadow': 'shadow', 'blur': 'blur',
        'shine': 'shine', 'reflection': 'reflection', 'neon': 'neon',
        '3d': '3d', 'emboss': 'emboss', 'outline': 'outline',
        'gradient': 'gradient-effect', 'fade': 'fade'
    }
    
    # Apply pattern detection
    for keyword, pattern in pattern_keywords.items():
        if keyword in prompt_lower and pattern not in design['patterns']:
            design['patterns'].append(pattern)
    
    # Apply shape detection
    for keyword, shape in shape_keywords.items():
        if keyword in prompt_lower and shape not in design['shapes']:
            design['shapes'].append(shape)
    
    # Apply texture detection
    for keyword, texture in texture_keywords.items():
        if keyword in prompt_lower and texture not in design['textures']:
            design['textures'].append(texture)
    
    # Apply effect detection
    for keyword, effect in effect_keywords.items():
        if keyword in prompt_lower and effect not in design['effects']:
            design['effects'].append(effect)
    
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
    
    # Generate visual elements based on detected features
    visual_elements = []
    
    # Add shapes as visual elements
    for shape in design['shapes']:
        visual_elements.append({
            'type': 'shape',
            'shape': shape,
            'size': 'medium',
            'position': 'random',
            'color': design['colors'][0] if design['colors'] else '#0066cc'
        })
    
    # Add pattern-based elements
    for pattern in design['patterns']:
        if pattern in ['star', 'circles', 'dots']:
            visual_elements.append({
                'type': 'pattern-element',
                'pattern': pattern,
                'density': 'medium',
                'size': 'small',
                'distribution': 'scattered'
            })
    
    # Add texture overlays
    for texture in design['textures']:
        visual_elements.append({
            'type': 'texture',
            'texture': texture,
            'opacity': 0.3,
            'blend_mode': 'overlay'
        })
    
    design['visualElements'] = visual_elements
    
    # Determine composition based on complexity
    complexity_indicators = ['complex', 'detailed', 'intricate', 'elaborate']
    simple_indicators = ['simple', 'clean', 'minimal', 'basic']
    
    if any(indicator in prompt_lower for indicator in complexity_indicators):
        design['complexity'] = 'high'
        design['layering'] = 'complex'
        design['composition'] = 'dynamic'
    elif any(indicator in prompt_lower for indicator in simple_indicators):
        design['complexity'] = 'low'
        design['layering'] = 'simple'
        design['composition'] = 'minimal'
    else:
        design['complexity'] = 'medium'
        design['layering'] = 'moderate'
        design['composition'] = 'balanced'
    
    # Adjust based on number of elements
    total_elements = len(design['patterns']) + len(design['shapes']) + len(design['effects'])
    if total_elements > 5:
        design['complexity'] = 'high'
        design['layering'] = 'complex'
    elif total_elements < 2:
        design['complexity'] = 'low'
        design['layering'] = 'simple'
    
    # Default values if none detected
    if not design['patterns']:
        design['patterns'] = ['modern']
    
    if not design['shapes'] and design['complexity'] != 'low':
        design['shapes'] = ['circle']
    
    if not design['effects'] and design['complexity'] == 'high':
        design['effects'] = ['glow']
    
    return design

