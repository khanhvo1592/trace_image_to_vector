import os
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import hashlib

def get_pdf_info(pdf_path):
    """Lấy thông tin chi tiết của file PDF"""
    try:
        # Đọc file với PyPDF2 để lấy kích thước
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            page = pdf.pages[0]
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            
        # Đọc file với PyMuPDF để lấy thông tin chi tiết hơn
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # Tính kích thước theo các đơn vị
        width_inch = width / 72
        height_inch = height / 72
        width_mm = width_inch * 25.4
        height_mm = height_inch * 25.4
        
        # Tính file size
        file_size = os.path.getsize(pdf_path)
        
        # Tính MD5 hash
        md5_hash = hashlib.md5()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                
        info = {
            'filename': os.path.basename(pdf_path),
            'size': {
                'bytes': file_size,
                'kb': file_size / 1024,
                'mb': file_size / (1024 * 1024)
            },
            'dimensions': {
                'points': (width, height),
                'inches': (width_inch, height_inch),
                'mm': (width_mm, height_mm)
            },
            'pages': len(doc),
            'md5': md5_hash.hexdigest(),
            'metadata': doc.metadata
        }
        
        doc.close()
        return info
        
    except Exception as e:
        print(f"Lỗi khi đọc file {pdf_path}: {str(e)}")
        return None

def compare_pdfs():
    # Đường dẫn tới các thư mục
    output_dir = "output"     # Thư mục chứa PDF được tạo mới
    compare_dir = "ok_file"   # Thư mục chứa PDF gốc để so sánh
    
    print("Đang so sánh các file PDF...\n")
    
    try:
        # Lấy danh sách file PDF trong thư mục output
        pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            # Tạo đường dẫn đầy đủ cho cả hai file PDF
            new_pdf_path = os.path.join(output_dir, pdf_file)
            orig_pdf_path = os.path.join(compare_dir, pdf_file)
            
            # Kiểm tra sự tồn tại của file gốc
            if not os.path.exists(orig_pdf_path):
                print(f"Không tìm thấy file gốc cho {pdf_file}")
                continue
            
            # Lấy thông tin của cả hai file PDF
            new_info = get_pdf_info(new_pdf_path)
            orig_info = get_pdf_info(orig_pdf_path)
            
            if new_info and orig_info:
                print(f"So sánh file: {pdf_file}")
                print("-" * 50)
                
                # So sánh kích thước file
                new_size = new_info['size']['kb']
                orig_size = orig_info['size']['kb']
                size_diff = new_size - orig_size
                size_percent = (abs(size_diff) / max(new_size, orig_size)) * 100
                
                print(f"\nKích thước file:")
                print(f"File mới: {new_size:.2f} KB")
                print(f"File gốc: {orig_size:.2f} KB")
                print(f"Chênh lệch: {abs(size_diff):.2f} KB")
                if size_diff > 0:
                    print(f"File mới lớn hơn {size_percent:.2f}% - Cần giảm {size_percent:.2f}%")
                elif size_diff < 0:
                    print(f"File mới nhỏ hơn {size_percent:.2f}%")
                
                # So sánh kích thước trang
                new_w, new_h = new_info['dimensions']['points']
                orig_w, orig_h = orig_info['dimensions']['points']
                width_diff = new_w - orig_w
                height_diff = new_h - orig_h
                
                print(f"\nKích thước trang (points):")
                print(f"File mới: {new_w:.2f} x {new_h:.2f}")
                print(f"File gốc: {orig_w:.2f} x {orig_h:.2f}")
                print(f"Chênh lệch: {abs(width_diff):.2f} x {abs(height_diff):.2f}")
                
                # Tính phần trăm chênh lệch
                if width_diff != 0:
                    width_percent = (abs(width_diff) / orig_w) * 100
                    if width_diff > 0:
                        print(f"Chiều rộng lớn hơn {width_percent:.2f}% - Cần giảm {width_percent:.2f}%")
                    else:
                        print(f"Chiều rộng nhỏ hơn {width_percent:.2f}%")
                
                if height_diff != 0:
                    height_percent = (abs(height_diff) / orig_h) * 100
                    if height_diff > 0:
                        print(f"Chiều cao lớn hơn {height_percent:.2f}% - Cần giảm {height_percent:.2f}%")
                    else:
                        print(f"Chiều cao nhỏ hơn {height_percent:.2f}%")
                
                print("\n" + "=" * 50 + "\n")
    
    except Exception as e:
        print(f"Lỗi khi so sánh PDF: {str(e)}")

if __name__ == "__main__":
    compare_pdfs()