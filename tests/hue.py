def calculateHue(color):
    r = int(color[1:3], 16) / 255
    g = int(color[3:5], 16) / 255
    b = int(color[5:7], 16) / 255

    minval = min(r, g, b)
    maxval = max(r, g, b)
    if (r > g and r > b):
        # red is max
        hue = (g - b) / (maxval - minval)
    elif (g > r and g > b):
        # green is max
        hue = 2 + (b - r) / (maxval - minval)
    elif (b > r and b > g):
        # blue is max
        hue = 4 + (r - g) / (maxval - minval)
    else:
        hue = 0

    hue *= 60;
    if (hue < 0): hue += 360

    return hue
    print(hue)

calculateHue("#FF2139")
