import json

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

def averageColor(colors):
    r = [int(c[1:3], 16) for c in colors]
    g = [int(c[3:5], 16) for c in colors]
    b = [int(c[5:7], 16) for c in colors]

    average = []
    average.append((r[0] + r[1]) / 2)
    average.append((g[0] + g[1]) / 2)
    average.append((b[0] + b[1]) / 2)
    brightness = (0.2126 * average[0] + 0.7152 * average[1] + 0.0722 * average[2])

    r_hex = []
    for a in average:
        r_hex.append(format(int(a), 'x'))

    average_color = "#" + "".join(r_hex).upper()
    return average_color, brightness


path = "src/settings.json"
with open(path) as json_file:
    settings = json.load(json_file)

colors = settings["Interface"]["colors"]
min_angle = 20
max_angle = 20
threshold_brightness = 127
colors_combinations = []

for c1 in colors:
    colors_copy = [c for c in colors]

    c1_hue = calculateHue(c1)

    for c2 in colors_copy:
        c2_hue = calculateHue(c2)
        angle_between = abs(c2_hue - c1_hue)
        if angle_between > 20 and angle_between < 90:
            average, brightness = averageColor([c1, c2])
            bright = brightness > threshold_brightness

            if not (c2, c1, bright) in colors_combinations:
                colors_combinations.append((c1, c2, bright))

with open('colors_combinations.json', 'w') as outfile:
    json.dump(colors_combinations, outfile)
