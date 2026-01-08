from PIL import Image, ImageDraw, ImageFont

def create_jersey():
    width, height = 600, 700
    img = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Jersey Rangi: Coca-Cola Qizili va Oltin hoshiya
    jersey_color = "#F40009"
    border_color = "#D4AF37"

    # Yelkalar va tana
    points = [
        (100, 50),  # Left Collar
        (500, 50),  # Right Collar
        (580, 200), # Right Sleeve End
        (480, 280), # Right Armpit
        (480, 700), # Bottom Right
        (120, 700), # Bottom Left
        (120, 280), # Left Armpit
        (20, 200)   # Left Sleeve End
    ]
    
    draw.polygon(points, fill=jersey_color, outline=border_color, width=5)

    # Logo joyi (Oq doira - oddiy)
    # draw.ellipse([350, 200, 420, 270], fill='white', outline=border_color) 

    # Bo'yin qismi (O'chirish uchun maska kerak emas, shunchaki shaffof rang bilan ustidan chizamiz - lekin PIL da bu qiyin)
    # Shuning uchun yangi rasm yaratib, maska bilan birlashtiramiz.
    
    mask = Image.new('L', (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    # V-Neck shakli (Qora = kesib tashlanadi)
    mask_draw.polygon([(200, 45), (400, 45), (300, 200)], fill=0)
    
    # Yakuniy natija
    final = Image.new('RGBA', (width, height), (0,0,0,0))
    final.paste(img, (0,0), mask=mask)
    
    # Oldiga chiziqlar (Design elements)
    f_draw = ImageDraw.Draw(final)
    # Oltin chiziqlar
    f_draw.line([(120, 280), (120, 700)], fill=border_color, width=3)
    f_draw.line([(480, 280), (480, 700)], fill=border_color, width=3)
    
    # Sponsor text (agar font bo'lmasa, shunchaki chiziq)
    try:
        # Oddiy font
        font = ImageFont.truetype("arial.ttf", 60)
        f_draw.text((300, 350), "FIFA", fill="white", font=font, anchor="mm")
        font_sm = ImageFont.truetype("arial.ttf", 30)
        f_draw.text((300, 400), "Coca-Cola", fill="white", font=font_sm, anchor="mm")
    except:
        pass

    final.save("src/assets/jersey.png")
    print("Jersey created at src/assets/jersey.png")

if __name__ == "__main__":
    create_jersey()
