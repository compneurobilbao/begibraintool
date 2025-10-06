import colorsys

def hsv_to_rgb_pixel(h, s, v):
    """Convierte valores HSV [0-1] a RGB [0-255]"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)
