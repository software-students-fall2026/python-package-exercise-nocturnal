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
    "watercolor": {
        "opacity": 0.4,
        "stroke": "none",
        "stroke_width": 0,
        "background": "#f3efe6",
        "saturation": 60,
        "lightness": 65,
        "texture": 0.1,
    },
    "acrylic": {
        "opacity": 0.95,
        "stroke": "white",
        "stroke_width": 2,
        "background": "#ece8e1",
        "saturation": 80,
        "lightness": 52,
        "texture": 0.08,
    },
    "neon": {
        "opacity": 0.0,
        "stroke": "petal color",
        "stroke_width": 2,
        "background": "navy",
        "saturation": 100,
        "lightness": 60,
        "texture": 0.0,
    },
    "charcoal": {
        "opacity": 0.35,
        "stroke": "#222222",
        "stroke_width": 3,
        "background": "#e6e3dc",
        "saturation": 0,
        "lightness": 35,
        "texture": 0.25
    },
    "pop": {
        "opacity": 1.0,
        "stroke": "black",
        "stroke_width": 4,
        "background": "yellow",
        "saturation": 100,
        "lightness": 55,
        "texture": 0.3
    }
}

species_names = list(Species)
art_styles = list(Styles)

def choose_flower(seed_hash: str):
    """turn a sha-256 hash into name of flower species and art style"""
    seed = bytes.fromhex(seed_hash)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash")
    # species determined by first byte, art style determined by fifth byte of seed_hash
    return species_names[seed[0] % len(species_names)], art_styles[seed[4] % len(art_styles)]

# set one canvas size 400 x 400
canvas = 400
# referenced https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorials
def render_flower_svg(seed_hash: str)-> str:
    """turn a sha-256 hash into flower drawn as svg text"""
    seed = bytes.fromhex(seed_hash)
    if len(seed) != 32:
        raise ValueError("expected a sha-256 hash")

    # name of flower and art style of seed_hash
    name, style = choose_flower(seed_hash)

    # get details for flower and art style
    flowername = Species[name]
    art = Styles[style]

    # hue (0-359) of color wheel, determined by second byte, hsl(hue, saturation%, lightness%) referenced from https://www.w3schools.com/html/html_colors_hsl.asp
    # can spread across color wheel
    hue = seed[1] * 360 // 256
    saturation = art["saturation"]
    lightness = art["lightness"]

    petal_color = f"hsl({hue}, {saturation}%, {lightness}%)"
    # go more around the wheel to get more colors
    second_color = f"hsl({(hue + 60) % 360}, {saturation}%, {lightness - 10}%)"
    center_color = f"hsl({(hue + 40) % 360}, {saturation}%, {lightness}%)"

    # neon use own petal color as outline, other styles do not
    if art["stroke"] == "petal color":
        outline_stroke = petal_color
    else:
        outline_stroke = art["stroke"]

    middle = canvas / 2
    petals = flowername["petals"]

    #start svg
    svg = f'<svg width="{canvas}" height= "{canvas}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<title>{name} in artstyle: {style}</title>'

    #background
    svg += f'<rect x="0" y="0" width="{canvas}" height="{canvas}" style="fill: {art["background"]};"/>'

    # for each layer
    for layer in range(flowername["layers"]):
        if layer == 0: 
            color = petal_color
        else:
            color = second_color

        # second layer of petal peeks out between gap of first layer
        rotate = layer * 180/petals

        # each petal
        for petal in range(petals):
            # petals are spread evenly 360 degrees
            angle = petal * 360 / petals + rotate
            svg += f'<ellipse cx="0" cy="-{flowername["ry"]}" rx="{flowername["rx"]}" ry="{flowername["ry"]} style="fill: {color}; stroke: {outline_stroke};" fill-opacity="{art["opacity"]}" stroke-width="{art["stroke_width"]}" transform="translate({middle}, {middle}) rotate({angle})"/>'

    # the pistil (middle of flowers)
    svg += f'<circle cx="{middle}" cy="{middle}" r="{flowername["center"]}" style="fill: {center_color}; stroke: {outline_stroke};" fill-opacity="{art["opacity"]}" stroke-width="{art["stroke_width"]}"/>'
    # close svg
    svg += "</svg>"
    return svg

