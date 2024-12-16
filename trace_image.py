import os
import cv2
import numpy as np
from PIL import Image
from xml.etree.ElementTree import Element, SubElement, ElementTree
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import fitz  # Thêm thư viện PyMuPDF

def create_svg_path_from_contours(contours):
    """Tạo SVG path data từ contours"""
    path_data = ""
    for contour in contours:
        epsilon = 0.0005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        points = approx.reshape(-1, 2)
        if len(points) > 0:
            path_data += f"M {points[0][0]:.2f},{points[0][1]:.2f} "
            for i in range(1, len(points)):
                path_data += f"L {points[i][0]:.2f},{points[i][1]:.2f} "
            path_data += "Z "
    
    return path_data

def preprocess_image(image):
    if len(image.shape) > 2:
        if image.shape[2] == 4:
            image = image[:, :, 3]
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    image = cv2.GaussianBlur(image, (5,5), 0.5)
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    
    return binary

def resize_pdf(input_path, output_path):
    """Scale PDF về kích thước 144x144"""
    try:
        # Đọc file PDF gốc
        doc = fitz.open(input_path)
        page = doc[0]
        
        # Lấy kích thước hiện tại
        rect = page.rect
        width = float(rect.width)
        height = float(rect.height)
        
        # Tính tỷ lệ scale
        scale = 144 / max(width, height)
        
        # Tạo PDF mới với kích thước 144x144
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=144, height=144)
        
        # Scale nội dung
        matrix = fitz.Matrix(scale, scale)
        new_page.show_pdf_page(new_page.rect, doc, 0, matrix)
        
        # Lưu file
        new_doc.save(output_path)
        
        # Đóng các file
        doc.close()
        new_doc.close()
        
        print(f"Đã resize PDF xuống 144x144")
        
    except Exception as e:
        print(f"Lỗi khi resize PDF: {str(e)}")

def image_to_pdf(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Hỗ trợ cả file PNG và JPG
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    temp_files = []  # Danh sách để lưu các file tạm thời
    
    try:
        for image_file in image_files:
            try:
                input_path = os.path.join(input_dir, image_file)
                output_filename = os.path.splitext(image_file)[0] + '.pdf'
                temp_pdf_path = os.path.join(output_dir, f"temp_{output_filename}")  # Thêm đường dẫn file tạm
                output_path = os.path.join(output_dir, output_filename)
                
                # Đọc ảnh và lấy DPI
                img = Image.open(input_path)
                dpi_x, dpi_y = img.info.get('dpi', (96, 96))  # Mặc định 96 DPI nếu không có thông tin
                img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
                
                if img is None:
                    print(f"Không thể đọc file {image_file}")
                    continue
                
                # Tính kích thước thực tế (inch)
                height, width = img.shape[:2]
                width_inch = width / dpi_x
                height_inch = height / dpi_y
                
                # Chuyển đổi inch sang points (1 inch = 72 points)
                width_pt = width_inch * 72
                height_pt = height_inch * 72
                
                # Xử lý ảnh
                processed = preprocess_image(img)
                
                # Tìm contours
                contours, _ = cv2.findContours(
                    processed,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_TC89_KCOS
                )
                
                # Lọc contours
                contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 10]
                
                # Tạo SVG với kích thước thực
                svg = Element('svg', {
                    'xmlns': 'http://www.w3.org/2000/svg',
                    'width': f'{width_pt}pt',
                    'height': f'{height_pt}pt',
                    'viewBox': f'0 0 {width} {height}',
                    'preserveAspectRatio': 'none'
                })
                
                g = SubElement(svg, 'g', {
                    'fill': 'black',
                    'stroke': 'none'
                })
                
                path_data = create_svg_path_from_contours(contours)
                if path_data:
                    path_element = SubElement(g, 'path', {
                        'd': path_data,
                        'style': 'fill-rule:evenodd'
                    })
                
                # Tạo file SVG tạm thời
                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
                    temp_path = tmp_svg.name
                    temp_files.append((tmp_svg, temp_path))
                    tree = ElementTree(svg)
                    tree.write(temp_path, encoding='utf-8', xml_declaration=True)
                
                # Chuyển SVG sang PDF tạm thời
                drawing = svg2rlg(temp_path)
                renderPDF.drawToFile(drawing, temp_pdf_path)  # Lưu vào file tạm
                
                print(f"Đã tạo PDF tạm thời")
                
                # Resize PDF xuống 144x144
                resize_pdf(temp_pdf_path, output_path)
                
                # Xóa file PDF tạm
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                
                print(f"Đã chuyển đổi {image_file} thành {output_filename}")
                
            except Exception as e:
                print(f"Lỗi khi xử lý {image_file}: {str(e)}")
        
    finally:
        # Dọn dẹp tất cả file tạm thời sau khi hoàn thành
        print("\nĐang dọn dẹp file tạm thời...")
        for tmp_svg, temp_path in temp_files:
            try:
                tmp_svg.close()
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                print(f"Lỗi khi xóa file tạm thời {temp_path}: {e}")
        print("Đã xóa tất cả file tạm thời")

# Thư mục input và output
input_directory = "input"
output_directory = "output"

print("Bắt đầu chuyển đổi...")
image_to_pdf(input_directory, output_directory)
print("Hoàn thành")