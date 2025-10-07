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
            'message': 'Enhanced AI design generated successfully'
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
    
    # Enhanced AI Knowledge Base with innovative features
    ai_knowledge = {
        'themes': {
            'fire': {
                'colors': ['#ff4500', '#ff0000', '#ffd700', '#ff6347'], 
                'patterns': ['flame', 'wave', 'radial', 'lightning'], 
                'shapes': ['triangle', 'diamond', 'flame-shape'],
                'textures': ['rough', 'glowing', 'ember'],
                'effects': ['glow', 'flicker', 'heat-wave'],
                'intensity': 'high',
                'photo_styles': ['abstract', 'macro', 'dynamic'],
                'advanced_patterns': ['fractal-flame', 'plasma', 'combustion']
            },
            'ocean': {
                'colors': ['#0066cc', '#00bfff', '#ffffff', '#20b2aa'], 
                'patterns': ['wave', 'flow', 'ripple', 'organic'], 
                'shapes': ['circle', 'oval', 'wave-form'],
                'textures': ['smooth', 'flowing', 'liquid'],
                'effects': ['shimmer', 'reflection', 'depth'],
                'intensity': 'medium',
                'photo_styles': ['fluid', 'underwater', 'seascape'],
                'advanced_patterns': ['voronoi-foam', 'caustics', 'tidal']
            },
            'forest': {
                'colors': ['#228b22', '#32cd32', '#8fbc8f', '#006400'], 
                'patterns': ['leaf', 'organic', 'branch', 'hexagonal'], 
                'shapes': ['hexagon', 'leaf-shape', 'tree'],
                'textures': ['natural', 'bark', 'moss'],
                'effects': ['shadow', 'dappled-light', 'growth'],
                'intensity': 'low',
                'photo_styles': ['botanical', 'macro', 'environmental'],
                'advanced_patterns': ['fibonacci-spiral', 'cellular-growth', 'dendrite']
            },
            'tech': {
                'colors': ['#00ffff', '#0080ff', '#ffffff', '#c0c0c0'], 
                'patterns': ['tech', 'circuit', 'geometric', 'mesh'], 
                'shapes': ['square', 'rectangle', 'hexagon'],
                'textures': ['metallic', 'digital', 'grid'],
                'effects': ['neon-glow', 'digital-pulse', 'scan-lines'],
                'intensity': 'high',
                'photo_styles': ['digital', 'glitch', 'cyberpunk'],
                'advanced_patterns': ['circuit-board', 'binary-matrix', 'neural-network']
            },
            'futuristic': {
                'colors': ['#00ffff', '#ff00ff', '#ffff00', '#000000'], 
                'patterns': ['circuit', 'tech', 'hexagonal', 'carbon'], 
                'shapes': ['hexagon', 'triangle', 'diamond'],
                'textures': ['metallic', 'holographic', 'carbon-fiber'],
                'effects': ['hologram', 'laser', 'energy-field'],
                'intensity': 'high',
                'photo_styles': ['holographic', 'quantum', 'dimensional'],
                'advanced_patterns': ['quantum-field', 'holographic-interference', 'energy-matrix']
            },
            'tribal': {
                'colors': ['#8b4513', '#d2691e', '#000000', '#ffffff'], 
                'patterns': ['tribal', 'organic', 'spiral'], 
                'shapes': ['triangle', 'diamond', 'spiral'],
                'textures': ['rough', 'earthy', 'carved'],
                'effects': ['shadow', 'depth', 'ancient'],
                'intensity': 'medium',
                'photo_styles': ['ethnic', 'cultural', 'primitive'],
                'advanced_patterns': ['sacred-geometry', 'totemic', 'ritualistic']
            },
            'carbon': {
                'colors': ['#2f2f2f', '#808080', '#000000', '#c0c0c0'], 
                'patterns': ['carbon', 'mesh', 'hexagonal'], 
                'shapes': ['hexagon', 'diamond', 'circle'],
                'textures': ['carbon-fiber', 'woven', 'metallic'],
                'effects': ['metallic-shine', 'depth', 'industrial'],
                'intensity': 'medium',
                'photo_styles': ['industrial', 'material', 'structural'],
                'advanced_patterns': ['carbon-weave', 'molecular-structure', 'composite']
            },
            'lightning': {
                'colors': ['#ffff00', '#9370db', '#000000', '#ffffff'], 
                'patterns': ['lightning', 'electric', 'zigzag'], 
                'shapes': ['jagged', 'bolt', 'spark'],
                'textures': ['electric', 'sharp', 'crackling'],
                'effects': ['flash', 'electric-glow', 'spark'],
                'intensity': 'high',
                'photo_styles': ['electric', 'storm', 'energy'],
                'advanced_patterns': ['lichtenberg', 'plasma-discharge', 'electric-field']
            },
            'sunset': {
                'colors': ['#ff6347', '#ffa500', '#ff69b4', '#ff4500'], 
                'patterns': ['gradient', 'soft', 'horizon'], 
                'shapes': ['circle', 'semi-circle', 'cloud'],
                'textures': ['soft', 'warm', 'glowing'],
                'effects': ['warm-glow', 'fade', 'silhouette'],
                'intensity': 'medium',
                'photo_styles': ['atmospheric', 'golden-hour', 'silhouette'],
                'advanced_patterns': ['atmospheric-scattering', 'cloud-formation', 'light-rays']
            },
            'galaxy': {
                'colors': ['#4b0082', '#8a2be2', '#00ced1', '#ff1493'], 
                'patterns': ['star', 'cosmic', 'spiral'], 
                'shapes': ['star', 'spiral', 'nebula'],
                'textures': ['cosmic', 'starry', 'nebulous'],
                'effects': ['twinkle', 'cosmic-glow', 'depth'],
                'intensity': 'high',
                'photo_styles': ['cosmic', 'deep-space', 'nebular'],
                'advanced_patterns': ['spiral-galaxy', 'stellar-formation', 'cosmic-web']
            },
            'arctic': {
                'colors': ['#87ceeb', '#ffffff', '#b0e0e6', '#e0ffff'], 
                'patterns': ['ice', 'crystal', 'snowflake'], 
                'shapes': ['hexagon', 'crystal', 'snowflake'],
                'textures': ['icy', 'crystalline', 'frozen'],
                'effects': ['frost', 'ice-shine', 'crystal-refraction'],
                'intensity': 'low',
                'photo_styles': ['crystalline', 'frozen', 'polar'],
                'advanced_patterns': ['ice-crystal', 'frost-fractal', 'snow-dendrite']
            },
            'desert': {
                'colors': ['#daa520', '#cd853f', '#f4a460', '#d2691e'], 
                'patterns': ['sand', 'dune', 'wave'], 
                'shapes': ['pyramid', 'dune', 'cactus'],
                'textures': ['sandy', 'rough', 'dry'],
                'effects': ['heat-shimmer', 'sand-drift', 'mirage'],
                'intensity': 'medium',
                'photo_styles': ['arid', 'landscape', 'geological'],
                'advanced_patterns': ['sand-ripple', 'erosion', 'geological-strata']
            },
            'vintage': {
                'colors': ['#8b4513', '#daa520', '#cd853f', '#f5deb3'], 
                'patterns': ['vintage', 'ornate', 'classic'], 
                'shapes': ['ornament', 'frame', 'scroll'],
                'textures': ['aged', 'worn', 'classic'],
                'effects': ['sepia', 'aged', 'vintage-filter'],
                'intensity': 'medium',
                'photo_styles': ['retro', 'nostalgic', 'heritage'],
                'advanced_patterns': ['art-deco', 'victorian', 'baroque']
            }
        },
        'emotions': {
            'aggressive': {'colors': ['#ff0000', '#000000', '#ff4500'], 'intensity': 'high', 'photo_styles': ['dramatic', 'high-contrast']},
            'calm': {'colors': ['#87ceeb', '#98fb98', '#f0f8ff'], 'intensity': 'low', 'photo_styles': ['serene', 'soft-focus']},
            'energetic': {'colors': ['#ff1493', '#00ff00', '#ffff00'], 'intensity': 'high', 'photo_styles': ['dynamic', 'motion-blur']},
            'professional': {'colors': ['#000080', '#ffffff', '#c0c0c0'], 'intensity': 'medium', 'photo_styles': ['corporate', 'clean']},
            'elegant': {'colors': ['#4b0082', '#ffd700', '#ffffff'], 'intensity': 'low', 'photo_styles': ['refined', 'luxury']},
            'bold': {'colors': ['#ff0000', '#ffff00', '#000000'], 'intensity': 'high', 'photo_styles': ['striking', 'pop-art']}
        },
        'sports': {
            'soccer': {'patterns': ['hexagon', 'net'], 'logos': ['ball', 'goal'], 'colors': ['#00ff00', '#ffffff'], 'photo_styles': ['action', 'field']},
            'basketball': {'patterns': ['court', 'lines'], 'logos': ['ball', 'hoop'], 'colors': ['#ff8c00', '#000000'], 'photo_styles': ['urban', 'court']},
            'football': {'patterns': ['field', 'yard'], 'logos': ['helmet', 'field'], 'colors': ['#8b4513', '#ffffff'], 'photo_styles': ['athletic', 'stadium']},
            'baseball': {'patterns': ['diamond', 'stitch'], 'logos': ['bat', 'ball'], 'colors': ['#ffffff', '#ff0000'], 'photo_styles': ['classic', 'americana']}
        },
        'photo_integration': {
            'abstract': ['fluid', 'flowing', 'organic', 'dynamic', 'expressive', 'painterly'],
            'geometric': ['structured', 'angular', 'precise', 'mathematical', 'crystalline', 'tessellated'],
            'nature': ['botanical', 'landscape', 'wildlife', 'macro', 'environmental', 'seasonal'],
            'urban': ['architectural', 'street', 'industrial', 'cityscape', 'modern', 'grunge'],
            'artistic': ['painterly', 'impressionistic', 'surreal', 'creative', 'experimental', 'avant-garde']
        },
        'advanced_patterns': {
            'fractals': ['mandelbrot', 'julia', 'sierpinski', 'dragon', 'tree', 'fern', 'coastline'],
            'tessellations': ['penrose', 'escher', 'islamic', 'honeycomb', 'voronoi', 'delaunay'],
            'optical': ['moire', 'interference', 'diffraction', 'holographic', 'prismatic', 'chromatic'],
            'organic': ['cellular', 'neural', 'vascular', 'coral', 'crystalline', 'growth', 'branching'],
            'digital': ['pixel', 'glitch', 'matrix', 'binary', 'circuit', 'data-visualization', 'algorithmic']
        },
        'color_harmonies': {
            'complementary': {'description': 'opposite colors on color wheel', 'creativity': 'high-contrast'},
            'triadic': {'description': 'three colors equally spaced', 'creativity': 'vibrant-balance'},
            'analogous': {'description': 'adjacent colors on wheel', 'creativity': 'harmonious-flow'},
            'split_complementary': {'description': 'base color plus two adjacent to complement', 'creativity': 'sophisticated-contrast'},
            'tetradic': {'description': 'four colors forming rectangle', 'creativity': 'complex-richness'},
            'monochromatic': {'description': 'variations of single hue', 'creativity': 'elegant-simplicity'}
        },
        'creative_mixing': {
            'gradient_types': ['linear', 'radial', 'conic', 'diamond', 'spiral', 'wave'],
            'blend_modes': ['multiply', 'screen', 'overlay', 'soft-light', 'hard-light', 'color-dodge'],
            'texture_overlays': ['noise', 'grain', 'fabric', 'paper', 'metal', 'glass', 'wood'],
            'dynamic_effects': ['parallax', 'morphing', 'particle-system', 'fluid-simulation']
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
    
    # Enhanced color detection with innovative mixing and photo-inspired palettes
    color_map = {
        # Basic colors
        'red': '#ff0000', 'crimson': '#dc143c', 'scarlet': '#ff2400', 'cherry': '#de3163',
        'blue': '#0066cc', 'navy': '#000080', 'royal': '#4169e1', 'sky': '#87ceeb', 'azure': '#007fff',
        'green': '#00ff00', 'forest': '#228b22', 'lime': '#32cd32', 'emerald': '#50c878', 'mint': '#98fb98',
        'yellow': '#ffff00', 'gold': '#ffd700', 'amber': '#ffbf00', 'lemon': '#fff700',
        'orange': '#ffa500', 'tangerine': '#ff8c00', 'coral': '#ff7f50', 'peach': '#ffcba4',
        'purple': '#800080', 'violet': '#ee82ee', 'indigo': '#4b0082', 'lavender': '#e6e6fa',
        'pink': '#ffc0cb', 'rose': '#ff007f', 'fuchsia': '#ff00ff', 'magenta': '#ff00ff',
        'black': '#000000', 'white': '#ffffff', 'gray': '#808080', 'grey': '#808080',
        'silver': '#c0c0c0', 'brown': '#a52a2a', 'cyan': '#00ffff', 'turquoise': '#40e0d0',
        
        # Photo-inspired colors
        'sunset': '#ff6b35', 'sunrise': '#ff9a56', 'ocean': '#006994', 'forest': '#2d5016',
        'desert': '#c19a6b', 'arctic': '#b6fcd5', 'volcanic': '#8b0000', 'cosmic': '#483d8b',
        'neon': '#39ff14', 'electric': '#7df9ff', 'plasma': '#ff073a', 'holographic': '#ff00ff',
        
        # Creative mixed colors
        'fire-orange': '#ff4500', 'ice-blue': '#b0e0e6', 'forest-green': '#228b22',
        'royal-purple': '#7851a9', 'electric-lime': '#ccff00', 'hot-pink': '#ff1493',
        'deep-sea': '#003366', 'lava-red': '#cf1020', 'cyber-cyan': '#00ffff',
        'quantum-violet': '#8a2be2', 'neural-blue': '#0047ab', 'plasma-pink': '#ff69b4',
        
        # Metallic and special effects
        'chrome': '#c0c0c0', 'copper': '#b87333', 'bronze': '#cd7f32', 'platinum': '#e5e4e2',
        'titanium': '#878681', 'iridescent': '#ff00ff', 'opal': '#a8c3bc', 'pearl': '#f0ead6'
    }
    
    # Photo-inspired color palettes
    photo_palettes = {
        'golden_hour': ['#ff6b35', '#f7931e', '#ffd700', '#ffb347'],
        'deep_ocean': ['#003366', '#006994', '#4682b4', '#87ceeb'],
        'forest_canopy': ['#2d5016', '#228b22', '#32cd32', '#90ee90'],
        'volcanic_fire': ['#8b0000', '#ff4500', '#ff6347', '#ffa500'],
        'arctic_aurora': ['#b6fcd5', '#00ff7f', '#40e0d0', '#7fffd4'],
        'cosmic_nebula': ['#483d8b', '#8a2be2', '#9370db', '#dda0dd'],
        'urban_neon': ['#39ff14', '#ff073a', '#00ffff', '#ff00ff'],
        'desert_sunset': ['#c19a6b', '#daa520', '#ff8c00', '#ff4500'],
        'cyber_matrix': ['#00ff00', '#39ff14', '#7fff00', '#adff2f'],
        'quantum_field': ['#7851a9', '#8a2be2', '#9932cc', '#ba55d3']
    }
    
    # Parse colors in order they appear in the prompt with photo palette integration
    detected_colors = []
    detected_palette = None
    prompt_words = prompt_lower.split()
    
    # Check for photo-inspired palette keywords
    palette_keywords = {
        'golden': 'golden_hour', 'sunset': 'golden_hour', 'warm': 'golden_hour',
        'ocean': 'deep_ocean', 'sea': 'deep_ocean', 'water': 'deep_ocean', 'marine': 'deep_ocean',
        'forest': 'forest_canopy', 'nature': 'forest_canopy', 'green': 'forest_canopy',
        'fire': 'volcanic_fire', 'lava': 'volcanic_fire', 'volcanic': 'volcanic_fire',
        'ice': 'arctic_aurora', 'arctic': 'arctic_aurora', 'cold': 'arctic_aurora',
        'space': 'cosmic_nebula', 'cosmic': 'cosmic_nebula', 'galaxy': 'cosmic_nebula',
        'neon': 'urban_neon', 'cyber': 'urban_neon', 'electric': 'urban_neon',
        'desert': 'desert_sunset', 'sand': 'desert_sunset', 'dune': 'desert_sunset',
        'matrix': 'cyber_matrix', 'digital': 'cyber_matrix', 'tech': 'cyber_matrix',
        'quantum': 'quantum_field', 'energy': 'quantum_field', 'plasma': 'quantum_field'
    }
    
    # Detect photo palette
    for keyword, palette_name in palette_keywords.items():
        if keyword in prompt_lower:
            detected_palette = palette_name
            break
    
    # Use photo palette if detected
    if detected_palette and detected_palette in photo_palettes:
        detected_colors = photo_palettes[detected_palette].copy()
    else:
        # Traditional color detection
        for i, word in enumerate(prompt_words):
            # Check for color names
            for color_name, hex_code in color_map.items():
                if word == color_name or (len(word) > 3 and color_name in word):
                    if hex_code not in detected_colors:
                        detected_colors.append(hex_code)
                    break
    
    # Creative color mixing for innovative combinations
    creative_keywords = ['creative', 'innovative', 'unique', 'artistic', 'experimental', 'mixed']
    if any(keyword in prompt_lower for keyword in creative_keywords):
        # Generate creative color combinations
        import random
        if not detected_colors:
            # Create innovative color combinations
            base_palettes = list(photo_palettes.values())
            palette1 = random.choice(base_palettes)
            palette2 = random.choice(base_palettes)
            # Mix colors from different palettes
            detected_colors = [palette1[0], palette2[1], palette1[2], palette2[0]]
        else:
            # Enhance existing colors with creative variations
            enhanced_colors = []
            for color in detected_colors[:2]:  # Take first 2 colors
                enhanced_colors.append(color)
                # Add a creative variation
                if color in ['#ff0000', '#dc143c']:  # Red variations
                    enhanced_colors.append('#ff073a')  # Plasma red
                elif color in ['#0000ff', '#0066cc']:  # Blue variations
                    enhanced_colors.append('#0047ab')  # Neural blue
                elif color in ['#00ff00', '#228b22']:  # Green variations
                    enhanced_colors.append('#39ff14')  # Electric green
            detected_colors = enhanced_colors if enhanced_colors else detected_colors
    
    # If colors were detected, use them in order
    if detected_colors:
        design['colors'] = detected_colors[:4]  # Limit to 4 colors for performance
    
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
    
    # Enhanced pattern and shape detection with advanced patterns
    pattern_keywords = {
        # Basic patterns
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
        'carbon': 'carbon', 'fiber': 'carbon', 'weave': 'carbon',
        
        # Advanced fractal patterns
        'fractal': 'fractal', 'mandelbrot': 'mandelbrot', 'julia': 'julia',
        'sierpinski': 'sierpinski', 'dragon': 'dragon-curve', 'tree': 'fractal-tree',
        'fern': 'fractal-fern', 'coastline': 'fractal-coastline',
        
        # Tessellation patterns
        'tessellation': 'tessellation', 'penrose': 'penrose-tiling', 'escher': 'escher-pattern',
        'islamic': 'islamic-pattern', 'voronoi': 'voronoi', 'delaunay': 'delaunay',
        
        # Optical and visual effects
        'moire': 'moire', 'interference': 'interference', 'diffraction': 'diffraction',
        'holographic': 'holographic', 'prismatic': 'prismatic', 'chromatic': 'chromatic',
        'optical': 'optical-illusion', 'illusion': 'optical-illusion',
        
        # Organic and biological patterns
        'cellular': 'cellular', 'neural': 'neural-network', 'vascular': 'vascular',
        'coral': 'coral-pattern', 'crystalline': 'crystalline', 'growth': 'growth-pattern',
        'branching': 'branching', 'dendrite': 'dendrite', 'fibonacci': 'fibonacci',
        
        # Digital and glitch patterns
        'pixel': 'pixel-art', 'glitch': 'glitch', 'matrix': 'matrix-pattern',
        'binary': 'binary', 'data': 'data-visualization', 'algorithmic': 'algorithmic',
        'noise': 'perlin-noise', 'procedural': 'procedural',
        
        # Photo-inspired patterns
        'texture': 'photo-texture', 'marble': 'marble-texture', 'wood': 'wood-grain',
        'fabric': 'fabric-weave', 'metal': 'metal-texture', 'stone': 'stone-texture',
        'water': 'water-ripple', 'smoke': 'smoke-pattern', 'cloud': 'cloud-formation'
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
    
    # Generate innovative visual elements based on detected features and creative options
    visual_elements = []
    
    # Photo integration keywords
    photo_keywords = ['photo', 'image', 'picture', 'visual', 'realistic', 'photographic']
    has_photo_request = any(keyword in prompt_lower for keyword in photo_keywords)
    
    # Add photo-inspired elements
    if has_photo_request or detected_palette:
        photo_style = 'abstract'
        if 'nature' in prompt_lower or 'forest' in prompt_lower:
            photo_style = 'nature'
        elif 'city' in prompt_lower or 'urban' in prompt_lower:
            photo_style = 'urban'
        elif 'geometric' in prompt_lower or 'structured' in prompt_lower:
            photo_style = 'geometric'
        elif 'artistic' in prompt_lower or 'creative' in prompt_lower:
            photo_style = 'artistic'
        
        visual_elements.append({
            'type': 'photo-integration',
            'style': photo_style,
            'blend_mode': 'multiply',
            'opacity': 0.4,
            'filter': 'artistic' if 'artistic' in prompt_lower else 'natural',
            'enhanced': False
        })
        

    
    # Add advanced pattern elements
    for pattern in design['patterns']:
        element_config = {
            'type': 'pattern-element',
            'pattern': pattern,
            'size': 'medium',
            'position': 'distributed'
        }
        
        # Advanced pattern configurations
        if pattern in ['fractal', 'mandelbrot', 'julia']:
            element_config.update({
                'type': 'fractal-pattern',
                'iterations': 100,
                'zoom': 1.5,
                'complexity': 'high',
                'fractal_depth': 5
            })
        elif pattern in ['voronoi', 'delaunay', 'tessellation']:
            element_config.update({
                'type': 'tessellation',
                'seed_points': 50,
                'variation': 'organic'
            })
        elif pattern in ['neural-network', 'cellular', 'growth-pattern']:
            element_config.update({
                'type': 'organic-pattern',
                'growth_rate': 0.7,
                'branching_factor': 3
            })
        elif pattern in ['glitch', 'matrix-pattern', 'binary']:
            element_config.update({
                'type': 'digital-effect',
                'intensity': 0.6,
                'randomness': 0.8
            })
        
        visual_elements.append(element_config)
    
    # Add shapes with enhanced properties
    for shape in design['shapes']:
        visual_elements.append({
            'type': 'enhanced-shape',
            'shape': shape,
            'size': 'dynamic',
            'position': 'calculated',
            'color': design['colors'][0] if design['colors'] else '#0066cc',
            'gradient': design.get('gradient', False),
            'animation': 'subtle' if 'dynamic' in prompt_lower else 'static',
            'glow_effect': False,
            'transform': {
                'scale_variation': 0.2,
                'rotation_speed': 'none'
            }
        })
    
    # Add innovative texture overlays
    for texture in design['textures']:
        texture_config = {
            'type': 'advanced-texture',
            'texture': texture,
            'opacity': 0.3,
            'blend_mode': 'overlay'
        }
        
        # Texture-specific enhancements
        if texture in ['metallic', 'chrome', 'copper']:
            texture_config.update({
                'reflection': 0.6,
                'shine': 0.8,
                'environment_map': True,
                'dynamic_reflection': False
            })
        elif texture in ['fabric', 'leather', 'wood']:
            texture_config.update({
                'bump_map': True,
                'surface_detail': 'high',
                'natural_variation': 0.4,
                'micro_details': False
            })
        elif texture in ['glass', 'crystal', 'diamond']:
            texture_config.update({
                'transparency': 0.7,
                'refraction': 1.5,
                'caustics': True,
                'prismatic_effects': False
            })
        
        visual_elements.append(texture_config)
    
    # Add creative effects based on complexity
    if design['complexity'] == 'high':
        # Add particle systems for high complexity
        visual_elements.append({
            'type': 'particle-system',
            'particle_count': 200,
            'behavior': 'flowing',
            'color_variation': True,
            'physics_simulation': False
        })
        
        # Add dynamic lighting
        visual_elements.append({
            'type': 'dynamic-lighting',
            'light_type': 'ambient',
            'color_temperature': 'warm' if 'warm' in prompt_lower else 'cool',
            'intensity': 0.5,
            'ray_tracing': False
        })
    
    # Add innovative blend modes and effects
    innovation_keywords = ['innovative', 'creative', 'unique', 'experimental']
    if any(keyword in prompt_lower for keyword in innovation_keywords):
        visual_elements.append({
            'type': 'creative-blend',
            'blend_modes': ['screen', 'color-dodge', 'hard-light', 'vivid-light', 'linear-burn'],
            'layer_effects': ['distortion', 'displacement', 'chromatic-aberration', 'holographic-interference'],
            'animation': 'morphing',
            'quantum_effects': False
        })
    
    design['visualElements'] = visual_elements
    
    # Add photo-realistic rendering hints
    if has_photo_request:
        design['renderingHints'] = {
            'quality': 'high',
            'anti_aliasing': True,
            'texture_filtering': 'anisotropic',
            'lighting_model': 'pbr',  # Physically Based Rendering
            'post_processing': ['bloom', 'tone_mapping', 'color_grading'],
            'ray_tracing': False,
            'global_illumination': False
        }
    
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
        if any(keyword in prompt_lower for keyword in ['creative', 'innovative', 'unique']):
            # Suggest creative patterns
            import random
            creative_patterns = ['fractal', 'voronoi', 'neural-network', 'glitch', 'holographic']
            design['patterns'] = [random.choice(creative_patterns)]
        else:
            design['patterns'] = ['modern']
    
    if not design['shapes'] and design['complexity'] != 'low':
        if any(keyword in prompt_lower for keyword in ['artistic', 'experimental']):
            # Add creative shapes
            import random
            creative_shapes = ['polygon', 'star', 'hexagon', 'diamond']
            design['shapes'] = [random.choice(creative_shapes)]
        else:
            design['shapes'] = ['circle']
    
    if not design['effects'] and design['complexity'] == 'high':
        design['effects'] = ['glow']
    
    # Add innovative suggestions for creative prompts
    if any(keyword in prompt_lower for keyword in ['innovative', 'creative', 'unique', 'experimental']):
        design['innovativeFeatures'] = {
            'suggested_enhancements': [
                'dynamic_color_shifting',
                'procedural_pattern_generation',
                'photo_texture_blending',
                'fractal_detail_layers',
                'holographic_effects'
            ],
            'creative_techniques': [
                'color_harmony_analysis',
                'golden_ratio_composition',
                'fibonacci_spiral_layout',
                'rule_of_thirds_positioning'
            ],
            'visual_innovation': True
        }
    
    # Add metadata for frontend processing
    design['metadata'] = {
        'ai_version': '2.0_enhanced',
        'features_used': {
            'photo_integration': has_photo_request,
            'palette_detection': detected_palette is not None,
            'creative_mixing': any(keyword in prompt_lower for keyword in creative_keywords),
            'advanced_patterns': any(pattern in ['fractal', 'voronoi', 'neural-network'] for pattern in design['patterns']),
            'innovative_mode': any(keyword in prompt_lower for keyword in ['innovative', 'creative', 'unique'])
        },
        'complexity_score': len(design['patterns']) + len(design['shapes']) + len(design['effects']),
        'color_count': len(design['colors']),
        'visual_elements_count': len(design.get('visualElements', []))
    }
    
    return design

