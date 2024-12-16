import os
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np

def get_image_size(image_path):
    """
    Lấy kích thước của file ảnh theo nhiều đơn vị đo
    """
    try:
        # Đọc ảnh bằng PIL để lấy DPI
        pil_img = Image.open(image_path)
        width, height = pil_img.size
        dpi_x, dpi_y = pil_img.info.get('dpi', (96, 96))
        
        # Tính kích thước thực tế
        width_inch = width / dpi_x
        height_inch = height / dpi_y
        
        # Chuyển đổi sang mm
        width_mm = width_inch * 25.4
        height_mm = height_inch * 25.4
        
        # Chuyển đổi sang points
        width_pt = width_inch * 72
        height_pt = height_inch * 72
        
        # Lấy dung lượng file
        file_size = os.path.getsize(image_path)
        
        info = {
            'file_name': os.path.basename(image_path),
            'pixel_size': (width, height),
            'dpi': (dpi_x, dpi_y),
            'points': (width_pt, height_pt),
            'inches': (width_inch, height_inch),
            'mm': (width_mm, height_mm),
            'file_size': file_size
        }
        
        return info
    
    except Exception as e:
        return {'error': f"Lỗi khi đọc file ảnh {image_path}: {str(e)}"}

def get_pdf_size(pdf_path):
    """
    Lấy kích thước của file PDF theo nhiều đơn vị đo
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        rect = page.rect
        
        # Kích thước theo points
        width_pt = rect.width
        height_pt = rect.height
        
        # Chuyển đổi sang các đơn vị khác
        width_inch = width_pt / 72
        height_inch = height_pt / 72
        
        width_mm = width_inch * 25.4
        height_mm = height_inch * 25.4
        
        # Lấy dung lượng file
        file_size = os.path.getsize(pdf_path)
        
        info = {
            'file_name': os.path.basename(pdf_path),
            'points': (width_pt, height_pt),
            'inches': (width_inch, height_inch),
            'mm': (width_mm, height_mm),
            'file_size': file_size
        }
        
        doc.close()
        return info
    
    except Exception as e:
        return {'error': f"Lỗi khi đọc file PDF {pdf_path}: {str(e)}"}

def compare_image_pdf_sizes(image_path, pdf_path):
    """
    So sánh kích thước giữa file ảnh gốc và file PDF
    """
    print("Đang so sánh kích thước ảnh gốc và PDF...\n")
    
    # Lấy thông tin của cả 2 file
    image_info = get_image_size(image_path)
    pdf_info = get_pdf_size(pdf_path)
    
    if 'error' in image_info or 'error' in pdf_info:
        if 'error' in image_info:
            print(image_info['error'])
        if 'error' in pdf_info:
            print(pdf_info['error'])
        return
    
    # In thông tin chi tiết của file ảnh
    print(f"File ảnh: {image_info['file_name']}")
    print(f"Kích thước pixel: {image_info['pixel_size'][0]} x {image_info['pixel_size'][1]}")
    print(f"DPI: {image_info['dpi'][0]} x {image_info['dpi'][1]}")
    print(f"Points: {image_info['points'][0]:.2f} x {image_info['points'][1]:.2f}")
    print(f"Inches: {image_info['inches'][0]:.2f} x {image_info['inches'][1]:.2f}")
    print(f"Millimeters: {image_info['mm'][0]:.2f} x {image_info['mm'][1]:.2f}")
    print(f"Dung lượng: {image_info['file_size']:,} bytes")
    
    # In thông tin chi tiết của file PDF
    print(f"\nFile PDF: {pdf_info['file_name']}")
    print(f"Points: {pdf_info['points'][0]:.2f} x {pdf_info['points'][1]:.2f}")
    print(f"Inches: {pdf_info['inches'][0]:.2f} x {pdf_info['inches'][1]:.2f}")
    print(f"Millimeters: {pdf_info['mm'][0]:.2f} x {pdf_info['mm'][1]:.2f}")
    print(f"Dung lượng: {pdf_info['file_size']:,} bytes")
    
    # Tính chênh lệch
    diff_width_mm = pdf_info['mm'][0] - image_info['mm'][0]
    diff_height_mm = pdf_info['mm'][1] - image_info['mm'][1]
    diff_size = pdf_info['file_size'] - image_info['file_size']
    
    print("\nChênh lệch (PDF - Ảnh):")
    print(f"Chiều rộng: {diff_width_mm:.2f} mm")
    print(f"Chiều cao: {diff_height_mm:.2f} mm")
    print(f"Dung lượng: {diff_size:,} bytes")
    
    # Phần trăm chênh lệch
    width_percent = (diff_width_mm / image_info['mm'][0]) * 100
    height_percent = (diff_height_mm / image_info['mm'][1]) * 100
    size_percent = (diff_size / image_info['file_size']) * 100
    
    print("\nChênh lệch (%):")
    print(f"Chiều rộng: {width_percent:.2f}%")
    print(f"Chiều cao: {height_percent:.2f}%")
    print(f"Dung lượng: {size_percent:.2f}%")

if __name__ == "__main__":
    # Đường dẫn đến file ảnh và PDF cần so sánh
    image_path = "input/2.png"
    pdf_path = "ok_file/2.pdf"
    
    compare_image_pdf_sizes(image_path, pdf_path) 