import os
import shutil
from pathlib import Path
from PIL import Image
from rembg import remove

class CardGenerator:
    def __init__(self):
        self.template_path = Path('src/data/templates/index.html')
        self.output_dir = Path('output/cards')
        self.temp_img_dir = Path('output/cards/images')
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_img_dir.mkdir(parents=True, exist_ok=True)

    def generate_card(self, user_photo_path, player_data, stats):
        """
        Generate FIFA card as HTML file with animations
        Returns: Path to the generated HTML file
        """
        try:
            # 1. Process User Image (Remove Background)
            print("🎨 Removing background...")
            # process_user_face already saves to output/cards/images/
            final_img_path = Path(self.process_user_face(user_photo_path))
            
            # HTML is in output/cards/
            # Image is in output/cards/images/
            # So relative path is just "images/filename"
            img_filename = final_img_path.name
            rel_path = f"images/{img_filename}"
            
            # 2. Read HTML Template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 3. Replace Placeholders
            replacements = {
                '{{NAME}}': player_data.get('name', 'PLAYER'),
                '{{OVR}}': str(stats.get('OVR', 99)),
                '{{POSITION}}': player_data.get('position', 'ST'),
                '{{IMAGE_PATH}}': rel_path,  # Simple relative path usually works best
                # Stats
                '{{PAC}}': str(stats.get('PAC', 99)),
                '{{SHO}}': str(stats.get('SHO', 99)),
                '{{PAS}}': str(stats.get('PAS', 99)),
                '{{DRI}}': str(stats.get('DRI', 99)),
                '{{DEF}}': str(stats.get('DEF', 99)),
                '{{PHY}}': str(stats.get('PHY', 99))
            }
            
            for key, value in replacements.items():
                html_content = html_content.replace(key, value)
            
            # 4. Save HTML File (Always overwrite current_card.html)
            output_filename = "current_card.html"
            output_path = self.output_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"✅ Card generated at: {output_path}")
            return str(output_path.resolve())

        except Exception as e:
            print(f"❌ Error generating card: {e}")
            raise e

    def process_user_face(self, image_path):
        """Remove background and composite with jersey"""
        try:
            img = Image.open(image_path).convert("RGBA")
            
            # Create output path
            filename = f"nobg_{os.path.basename(image_path)}"
            output_path = self.temp_img_dir / filename
            output_path = output_path.with_suffix('.png') 
            
            # 1. Remove background
            print("🎨 Removing background...")
            img_no_bg = remove(img)
            
            # 2. Composite with Jersey
            jersey_path = 'src/assets/jersey.png'
            if os.path.exists(jersey_path):
                print("👕 Applying Jersey...")
                jersey = Image.open(jersey_path).convert("RGBA")
                
                # Resize user to fit nicely behind the jersey
                # We want head to be visible above the collar
                # Jersey dimensions are 600x700, Neck is roughly centered top
                
                # Scale user image so head fits
                # Assuming standard selfie ratio, let's make user 60% of jersey width
                scale_factor = 0.55
                target_w = int(jersey.width * scale_factor)
                ratio = target_w / img_no_bg.width
                target_h = int(img_no_bg.height * ratio)
                
                user_resized = img_no_bg.resize((target_w, target_h), Image.Resampling.LANCZOS)
                
                # Create empty canvas size of jersey
                final_comp = Image.new("RGBA", jersey.size, (0,0,0,0))
                
                # Position user: Centered horizontally, vertically aligned so chin is near neck hole bottom
                # Neck hole bottom is around Y=200 in our generated jersey
                # We place user slightly higher
                pos_x = (jersey.width - user_resized.width) // 2
                pos_y = 50 # Adjust to make head appear in neck hole
                
                # Paste User First (Behind)
                final_comp.paste(user_resized, (pos_x, pos_y), user_resized)
                
                # Paste Jersey Second (In Front)
                final_comp.paste(jersey, (0,0), jersey)
                
                final_comp.save(output_path, "PNG")
            else:
                print("⚠️ Jersey template not found, using raw cutout")
                img_no_bg.save(output_path, "PNG")
            
            return str(output_path)
        except Exception as e:
            print(f"Bg removal/Composite failed: {e}")
            return image_path # Fallback

