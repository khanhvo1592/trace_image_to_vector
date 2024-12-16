import os
from PyPDF2 import PdfReader
from PIL import Image

def get_pdf_size(pdf_path):
    """Lấy kích thước của file PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            page = pdf.pages[0]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            return width, height
    except Exception as e:
        print(f"Lỗi khi đọc file {pdf_path}: {str(e)}")
        return None

def get_image_size(image_path):
    """Lấy kích thước của file ảnh"""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        print(f"Lỗi khi đọc file {image_path}: {str(e)}")
        return None

def compare_sizes():
    # Đường dẫn tới các thư mục
    output_dir = "output"    # Thư mục chứa file PDF được tạo
    input_dir = "ok_file"    # Thư mục chứa file ảnh gốc để so sánh
    
    print("Đang so sánh kích thước PDF...")
    
    # Lấy danh sách file trong thư mục
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files:
        # Tạo đường dẫn đầy đủ
        pdf_path = os.path.join(output_dir, pdf_file)
        image_file = os.path.splitext(pdf_file)[0] + '.png'
        image_path = os.path.join(input_dir, image_file)
        
        # Lấy kích thước
        pdf_size = get_pdf_size(pdf_path)
        image_size = get_image_size(image_path)
        
        if pdf_size and image_size:
            pdf_width, pdf_height = pdf_size
            img_width, img_height = image_size
            
            # Tính phần trăm chênh lệch
            width_diff = abs(pdf_width - img_width) / img_width * 100
            height_diff = abs(pdf_height - img_height) / img_height * 100
            
            print(f"\nSo sánh kích thước cho {pdf_file}:")
            print(f"PDF: {pdf_width:.2f}x{pdf_height:.2f}")
            print(f"Ảnh: {img_width}x{img_height}")
            print(f"Chênh lệch (%):")
            print(f"Chiều rộng: {width_diff:.2f}%")
            print(f"Chiều cao: {height_diff:.2f}%")

if __name__ == "__main__":
    compare_sizes()