import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

# Configuración
width, height = 600, 200  # Tamaño ajustable (ideal para banner)
chars = "01アイウエオABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
font_size = 14
frames = 30  # Número de frames para el GIF
background_color = (0, 0, 0)  # Fondo negro
text_color = (0, 255, 0)  # Verde Matrix

# Crear frames
images = []
for _ in range(frames):
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Usar una fuente monospace (asegúrate de tenerla instalada)
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", font_size)
    except:
        font = ImageFont.load_default()  # Fuente por defecto si no existe
    
    # Generar caracteres aleatorios en posiciones verticales
    for x in range(0, width, font_size + 2):
        for y in range(0, height, font_size + 2):
            char = np.random.choice(list(chars))
            draw.text((x, y), char, fill=text_color, font=font)
    
    images.append(img)

# Guardar GIF
imageio.mimsave('matrix_banner.gif', images, duration=0.1, loop=0)  # loop=0: infinito
print("¡GIF generado como 'matrix_banner.gif'!")
