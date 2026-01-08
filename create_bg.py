from PIL import Image, ImageDraw

# Create a dark background with subtle texture suitable for "Coca-Cola x FIFA" theme
width, height = 1920, 1080
image = Image.new('RGB', (width, height), color=(10, 10, 10))
draw = ImageDraw.Draw(image)

# Add subtle red gradient/glow at corners
for i in range(width):
    # Very inefficient but simple gradient loop for demo
    # Just creating a dark base
    pass

# Let's just create a Hex-pattern or simple grid
# Draw subtle dark red lines
for x in range(0, width, 50):
    draw.line([(x, 0), (x, height)], fill=(30, 0, 0), width=1)

for y in range(0, height, 50):
    draw.line([(0, y), (width, y)], fill=(30, 0, 0), width=1)

# Add a vignette effect (simple circle darkening)
# ... skipping complex effects for speed, basic grid is enough to stop the warning
# and look better than plain black.

output_path = 'src/assets/bg_pattern.png'
image.save(output_path)
print(f"Background created at {output_path}")
