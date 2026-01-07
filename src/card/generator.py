import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove
import numpy as np


class CardGenerator:
    def __init__(self):
        self.templates = {
            'bg': 'src/data/templates/male_card.png'
        }
        
        # Try to use common Windows fonts as defaults
        self.fonts = {
            'main': 'C:/Windows/Fonts/segoeuib.ttf', # Segoe UI Bold
            'bold': 'C:/Windows/Fonts/arialbd.ttf'   # Arial Bold
        }
        
        self.gold_color = (233, 204, 116) # #e9cc74

    def generate_card(self, user_photo_path, player_data, stats):
        """Generate FIFA card using native Pillow implementation (High Quality)"""
        # 1. Load Background (Source is 495x800)
        if os.path.exists(self.templates['bg']):
            card = Image.open(self.templates['bg']).convert('RGBA')
            width, height = card.size
        else:
            width, height = 495, 800
            card = Image.new('RGBA', (width, height), color=(20, 20, 20, 255))
            draw = ImageDraw.Draw(card)
            draw.rectangle([10, 10, width-10, height-10], outline=self.gold_color, width=5)

        # 2. Process and Paste User Face
        user_face = self.process_user_face(user_photo_path)
        # Resize face to fit (scaled from 200/300 * 495 = 330)
        face_size = int(width * 0.67)
        user_face = user_face.resize((face_size, face_size), Image.Resampling.LANCZOS)
        # Position: right-ish top
        face_x = int(width * 0.3)
        face_y = int(height * 0.15)
        card.paste(user_face, (face_x, face_y), user_face)

        # 3. Add Rating and Position (Top Left)
        self.draw_text(card, str(stats.get('OVR', 99)), (int(width*0.18), int(height*0.12)), font_size=int(height*0.1), color=self.gold_color, anchor="mm")
        self.draw_text(card, player_data.get('position', 'ST'), (int(width*0.18), int(height*0.22)), font_size=int(height*0.05), color=self.gold_color, anchor="mm")

        # 4. Add Player Name (Center Bottom)
        name = player_data.get('name', 'PLAYER').upper()
        self.draw_text(card, name, (width//2, int(height*0.58)), font_size=int(height*0.06), color=self.gold_color, anchor="mm")

        # 5. Add Stats (2 columns)
        stat_y_start = int(height * 0.65)
        stat_spacing = int(height * 0.05)
        col1_x = int(width * 0.25)
        col2_x = int(width * 0.6)
        
        # Col 1
        self.draw_stat(card, "PAC", stats.get('PAC', stats.get('DIV', 80)), (col1_x, stat_y_start), height)
        self.draw_stat(card, "SHO", stats.get('SHO', stats.get('HAN', 80)), (col1_x, stat_y_start + stat_spacing), height)
        self.draw_stat(card, "PAS", stats.get('PAS', stats.get('KIC', 80)), (col1_x, stat_y_start + 2*stat_spacing), height)
        
        # Col 2
        self.draw_stat(card, "DRI", stats.get('DRI', stats.get('REF', 80)), (col2_x, stat_y_start), height)
        self.draw_stat(card, "DEF", stats.get('DEF', stats.get('SPD', 80)), (col2_x, stat_y_start + stat_spacing), height)
        self.draw_stat(card, "PHY", stats.get('PHY', stats.get('POS', 80)), (col2_x, stat_y_start + 2*stat_spacing), height)

        # 6. Save Result
        output_path = f"output/cards/card_{os.path.basename(user_photo_path)}.png"
        card.save(output_path, "PNG")
        
        return output_path

    def draw_stat(self, image, label, value, position, card_height):
        """Helper to draw a single stat line"""
        val_size = int(card_height * 0.045)
        lbl_size = int(card_height * 0.04)
        # Value (Bold)
        self.draw_text(image, str(value), position, font_size=val_size, color=self.gold_color, bold=True, anchor="rm")
        # Label
        self.draw_text(image, label, (position[0] + int(card_height*0.02), position[1]), font_size=lbl_size, color=self.gold_color, anchor="lm")

    def draw_text(self, image, text, position, font_size=20, color='white', anchor=None, bold=False):
        """Utility to draw text with font handling"""
        draw = ImageDraw.Draw(image)
        font_key = 'bold' if bold else 'main'
        
        try:
            # Check if custom font path exists, else use standard ones
            font_path = self.fonts[font_key]
            if not os.path.exists(font_path):
                 # Try local project fonts first
                 local_path = f"src/assets/fonts/{'arial_bold.ttf' if bold else 'fifa_font.ttf'}"
                 if os.path.exists(local_path):
                     font_path = local_path
                 else:
                     font_path = "arialbd.ttf" if bold else "arial.ttf"
                     
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        draw.text(position, text, font=font, fill=color, anchor=anchor)

    def process_user_face(self, image_path):
        """Remove background and process face"""
        img = Image.open(image_path)
        img_no_bg = remove(img)
        return img_no_bg
