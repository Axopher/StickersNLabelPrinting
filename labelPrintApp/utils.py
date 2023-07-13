def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)
    return red, green, blue

  