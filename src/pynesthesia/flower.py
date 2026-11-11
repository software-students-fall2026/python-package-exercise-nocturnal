Species = {
    #number of petals, layers, petal radius of width + length (pixel), radius of center (pixel)
    "sunflower": {
        "petals": 34,
        "layers": 2,
        "rx": 9,
        "ry": 85,
        "center": 42
    },
    "lily": {
        "petals": 6,
        "layers": 1,
        "rx": 32,
        "ry": 85,
        "center": 12
    },   
    "rose": {
        "petals": 8,
        "layers": 2,
        "rx": 40,
        "ry": 55,
        "center": 10
    },   
    "orchid": {
        "petals": 5,
        "layers": 1,
        "rx": 52,
        "ry": 70,
        "center": 16
    },    
    "lavender":{
        "petals": 12,
        "layers": 1,
        "rx": 8,
        "ry": 60,
        "center": 8
    }
 }

Styles = {
    # art mediums
    "watercolor": {"opacity": 0.4, "stroke": "none", "stroke_width": 0, "background": "#f3efe6", "saturation": 60, "lightness": 65},
    "acrylic": {"opacity": 0.95, "stroke": "white", "stroke_width": 2, "background": "#ece8e1", "saturation": 80, "lightness": 52},
    "neon": {"opacity": 0.0, "stroke": "petal color", "stroke_width": 2, "background": "navy", "saturation": 100, "lightness": 60},
    "charcoal": {"opacity": 0.35, "stroke": "#222222", "stroke_width": 3, "background": "#e6e3dc", "saturation": 0, "lightness": 35},
    "pop": {"opacity": 1.0, "stroke": "black", "stroke_width": 4, "background": "yellow", "saturation": 100, "lightness": 55}
}

species_names = list(Species)
art_styles = list(Styles)

def choose_flower(seed_hash: str):
    """turn a sha-256 hash into name of flower species"""
    seed = bytes.fromhex(seed_hash)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash")
    # species determined by first byte, art style determined by fifth byte of seed_hash
    return species_names[seed[0] % len(species_names)], art_styles[seed[4] % len(art_styles)]
