import os
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove
import numpy as np
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QEventLoop, QUrl, QSize
from PySide6.QtGui import QPageLayout, QPageSize


class CardGenerator:
    def __init__(self):
        self.templates = {
            'html': 'src/data/templates/index.html'
        }
        
        self.fonts = {
            'title': 'src/assets/fonts/fifa_font.ttf',
            'stats': 'src/assets/fonts/arial_bold.ttf'
        }

    def generate_card(self, user_photo_path, player_data, stats):
        """Generate FIFA card using HTML template"""
        # 1. Process user photo (remove background)
        user_face = self.process_user_face(user_photo_path)
        
        # Save processed face temporarily to use in HTML
        processed_face_path = f"output/captured/processed_{os.path.basename(user_photo_path)}"
        user_face.save(processed_face_path)
        
        # Convert image to base64 for HTML
        with open(processed_face_path, "rb") as f:
            face_base64 = base64.b64encode(f.read()).decode()
        photo_url = f"data:image/png;base64,{face_base64}"

        # 2. Read and populate HTML template
        with open(self.templates['html'], 'r', encoding='utf-8') as f:
            template = f.read()
            
        # Replace placeholders
        html_content = template.replace('{{rating}}', str(stats.get('OVR', 99)))
        html_content = html_content.replace('{{position}}', player_data.get('position', 'ST'))
        html_content = html_content.replace('{{name}}', player_data.get('name', 'PLAYER'))
        html_content = html_content.replace('{{photo_url}}', photo_url)
        
        # Stats
        html_content = html_content.replace('{{pac}}', str(stats.get('PAC', stats.get('DIV', 80))))
        html_content = html_content.replace('{{sho}}', str(stats.get('SHO', stats.get('HAN', 80))))
        html_content = html_content.replace('{{pas}}', str(stats.get('PAS', stats.get('KIC', 80))))
        html_content = html_content.replace('{{dri}}', str(stats.get('DRI', stats.get('REF', 80))))
        html_content = html_content.replace('{{def}}', str(stats.get('DEF', stats.get('SPD', 80))))
        html_content = html_content.replace('{{phy}}', str(stats.get('PHY', stats.get('POS', 80))))
        
        # URLs (These remain but user can change them in HTML for offline)
        html_content = html_content.replace('{{nation_url}}', 'https://selimdoyranli.com/cdn/fut-player-card/img/argentina.svg')
        html_content = html_content.replace('{{club_url}}', 'https://selimdoyranli.com/cdn/fut-player-card/img/barcelona.svg')

        # 3. Render HTML to Image using QWebEngineView
        output_path = f"output/cards/card_{os.path.basename(user_photo_path)}.png"
        self.render_to_image(html_content, output_path)
        
        return output_path

    def render_to_image(self, html_content, output_path):
        """Headless rendering of HTML to PNG"""
        view = QWebEngineView()
        # FUT card in index.html is 300x485
        view.setFixedSize(300, 485) 
        
        loop = QEventLoop()
        view.loadFinished.connect(loop.quit)
        view.setHtml(html_content)
        loop.exec() # Wait for load
        
        # Capture the widget
        pixmap = view.grab()
        pixmap.save(output_path, "PNG")
        view.deleteLater()

    def process_user_face(self, image_path):
        """Remove background and process face"""
        img = Image.open(image_path)
        img_no_bg = remove(img)
        return img_no_bg
