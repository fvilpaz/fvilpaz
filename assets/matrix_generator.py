import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

# Configuración
width, height = 600, 200 
chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ0123456789ｱｲｳｴｵｶｷｸｹｺ"
font_size = 14
frames = 30 
background_color = (0, 0, 0)
text_color = (0, 255, 0)

images = []
for _ in range(frames):
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    try:        
        font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    for x in range(0, width, font_size + 2):
        for y in range(0, height, font_size + 2):
            char = np.random.choice(list(chars))
            draw.text((x, y), char, fill=text_color, font=font)
    
    images.append(img)

imageio.mimsave('matrix_banner.gif', images, duration=0.1, loop=0)
print("¡GIF generado! Ahora verás muchos más caracteres japoneses.")
