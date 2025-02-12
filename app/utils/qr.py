import qrcode
import os
from flask import current_app

def generate_memorial_qr(memorial_id, url):
    """Generate QR code for a memorial"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Create directory if it doesn't exist
    qr_dir = os.path.join(current_app.static_folder, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Save QR code
    filename = f'memorial_{memorial_id}.png'
    file_path = os.path.join(qr_dir, filename)
    qr_image.save(file_path)
    
    return filename 