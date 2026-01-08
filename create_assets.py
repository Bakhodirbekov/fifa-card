from PIL import Image, ImageDraw, ImageFont

def create_assets():
    # 1. Uzbekistan Flag (300x200)
    flag = Image.new('RGB', (300, 200), 'white')
    draw = ImageDraw.Draw(flag)
    
    # Colors
    blue = "#0099B5"
    white = "#FFFFFF"
    green = "#1EB53A"
    red = "#CE1126"
    
    # Stripes
    draw.rectangle([0, 0, 300, 66], fill=blue)
    draw.rectangle([0, 66, 300, 70], fill=red) # Red line top
    draw.rectangle([0, 70, 300, 130], fill=white)
    draw.rectangle([0, 130, 300, 134], fill=red) # Red line bottom
    draw.rectangle([0, 134, 300, 200], fill=green)
    
    # Moon and Stars (Simplified as white circle and dots)
    draw.ellipse([20, 15, 50, 45], fill=white) # Moon shape
    draw.ellipse([25, 15, 55, 45], fill=blue)  # Overlay to make crescent
    
    flag.save("src/assets/flag_uz.png")
    print("Flag created.")
    
    # 2. Coca-Cola Logo (Square icon style)
    # White background, Red text
    logo = Image.new('RGBA', (200, 200), (0,0,0,0)) # Transparent
    l_draw = ImageDraw.Draw(logo)
    
    # Red Circle
    l_draw.ellipse([10, 10, 190, 190], fill="#F40009")
    
    # Text "Coke" (Simple representation)
    try:
        font = ImageFont.truetype("arial.ttf", 50)
        l_draw.text((100, 100), "Coke", fill="white", font=font, anchor="mm")
    except:
        l_draw.text((60, 90), "Coca", fill="white")
        l_draw.text((60, 110), "Cola", fill="white")
        
    logo.save("src/assets/coke_logo.png")
    print("Logo created.")

if __name__ == "__main__":
    create_assets()
