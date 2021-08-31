with open("colors") as f:
    content = f.readlines()

colors = [c.strip().upper() for c in content]
print(colors)
