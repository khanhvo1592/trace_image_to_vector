import os
import cv2
import numpy as np
from PIL import Image
from xml.etree.ElementTree import Element, SubElement, ElementTree
import tempfile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import fitz  #PyMuPDF
import shutil

def create_svg_path_from_contours(contours):
    """Tạo SVG path data từ contours với độ chính xác cao"""
    path_data = []
    for contour in contours:
        # Lọc contours quá nhỏ
        if cv2.contourArea(contour) <= 5:
            continue
            
        epsilon = 0.0001 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        points = approx.reshape(-1, 2)
        
        if len(points) > 0:
            # Bắt đầu từ điểm đầu tiên
            path_data.append(f"M {points[0][0]:.3f},{points[0][1]:.3f}")
            for point in points[1:]:
                path_data.append(f"L {point[0]:.3f},{point[1]:.3f}")
            path_data.append("Z")
    
    return " ".join(path_data)

def remove_white_background(input_path, output_path):
    """Bước 1: Loại bỏ màu trắng, giữ màu đen trong PNG"""
    try:
        # Đọc ảnh gốc
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        
        # Tạo thư mục debug nếu chưa có
        debug_dir = "debug_output"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        
        # Kiểm tra và chuyển đổi sang RGBA
        if len(img.shape) == 2:  # Grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        elif len(img.shape) == 3 and img.shape[2] == 3:  # RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        
        # Tách các kênh màu
        b, g, r, a = cv2.split(img)
        
        # Tạo mask cho màu trắng với ngưỡng cao hơn
        white_mask = (b >= 245) & (g >= 245) & (r >= 245)
        
        # Xử lý viền bằng morphology
        kernel = np.ones((3,3), np.uint8)
        white_mask = cv2.dilate(white_mask.astype(np.uint8), kernel, iterations=1)
        
        # Debug: Lưu mask màu trắng
        cv2.imwrite(os.path.join(debug_dir, "white_mask.png"), white_mask.astype(np.uint8) * 255)
        
        # Cập nhật alpha channel
        a[white_mask == 1] = 0
        
        # Gộp các kênh lại
        result = cv2.merge([b, g, r, a])
        
        # Lưu ảnh PNG với alpha channel và chất lượng cao
        cv2.imwrite(output_path, result, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        
        # Debug: Lưu kết quả
        cv2.imwrite(os.path.join(debug_dir, "result.png"), result)
        
        return True
        
    except Exception as e:
        print(f"Lỗi khi xử lý ảnh trong suốt: {str(e)}")
        return False

def calculate_dimensions(width, height, target_size=600):
    """Tính toán kích thước mới giữ nguyên tỷ lệ"""
    aspect_ratio = width / height
    
    if width >= height:
        # Ảnh ngang
        if aspect_ratio >= 2:  # Tỷ lệ >= 2:1
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
        else:
            new_height = target_size
            new_width = int(target_size * aspect_ratio)
    else:
        # Ảnh dọc
        if aspect_ratio <= 0.5:  # Tỷ lệ <= 1:2
            new_height = target_size
            new_width = int(target_size * aspect_ratio)
        else:
            new_width = target_size
            new_height = int(target_size / aspect_ratio)
    
    return new_width, new_height

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

def create_svg_with_transparency(img, new_width, new_height):
    """Tạo SVG với màu đen và phần trong suốt (cả bên trong) thành trắng"""
    svg = Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'width': '144pt',
        'height': '144pt',
        'viewBox': f'0 0 {new_width} {new_height}',
        'preserveAspectRatio': 'xMidYMid meet'
    })
    
    # Xử lý alpha channel và màu
    alpha = img[:, :, 3]
    bgr = img[:, :, :3]
    
    # 1. Tạo mask cho phần màu đen (không trong suốt và tối)
    black_pixels = (np.mean(bgr, axis=2) < 128) & (alpha > 0)
    black_mask = black_pixels.astype(np.uint8) * 255
    
    # 2. Tạo mask cho phần trong suốt
    transparent_mask = (alpha == 0).astype(np.uint8) * 255
    
    # Debug: Lưu các mask
    cv2.imwrite(os.path.join("debug_output", "black_mask.png"), black_mask)
    cv2.imwrite(os.path.join("debug_output", "transparent_mask.png"), transparent_mask)
    
    # Thêm background trắng
    SubElement(svg, 'rect', {
        'width': '100%',
        'height': '100%',
        'fill': 'white'
    })
    
    # Tìm tất cả contours cho phần màu đen, bao gồm cả lỗ bên trong
    black_contours, hierarchy = cv2.findContours(
        black_mask,
        cv2.RETR_CCOMP,  # Thay đổi từ EXTERNAL sang CCOMP để lấy cả contours bên trong
        cv2.CHAIN_APPROX_TC89_KCOS
    )
    
    if black_contours:
        g_black = SubElement(svg, 'g', {
            'fill': 'black',
            'stroke': 'none'
        })
        
        # Tạo path phức hợp với các lỗ
        path_data = []
        
        # Xử lý từng contour theo hierarchy
        for i, contour in enumerate(black_contours):
            if cv2.contourArea(contour) <= 5:  # Bỏ qua contours quá nhỏ
                continue
                
            epsilon = 0.0001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            points = approx.reshape(-1, 2)
            
            if len(points) > 0:
                # Kiểm tra nếu là contour ngoài cùng
                if hierarchy[0][i][3] == -1:  # Parent ID = -1 nghĩa là contour ngoài
                    points_str = create_path_from_points(points)
                else:  # Contour trong (lỗ)
                    # Đảo ngược thứ tự điểm để tạo lỗ
                    points = points[::-1]
                    points_str = create_path_from_points(points)
                
                path_data.append(points_str)
        
        if path_data:
            SubElement(g_black, 'path', {
                'd': " ".join(path_data),
                'fill-rule': 'evenodd'  # Quan trọng cho việc xử lý lỗ
            })
    
    return svg

def create_path_from_points(points):
    """Tạo path string từ mảng points"""
    path = [f"M {points[0][0]:.3f},{points[0][1]:.3f}"]
    for point in points[1:]:
        path.append(f"L {point[0]:.3f},{point[1]:.3f}")
    path.append("Z")
    return " ".join(path)

def image_to_pdf(input_dir, output_dir):
    """Chuyển đổi ảnh thành PDF và xóa file tạm"""
    # Khởi tạo danh sách file tạm
    png_temp_files = []
    svg_temp_files = []
    pdf_temp_files = []
    
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Lấy danh sách file ảnh
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    try:
        for image_file in image_files:
            try:
                input_path = os.path.join(input_dir, image_file)
                output_filename = os.path.splitext(image_file)[0] + '.pdf'
                output_path = os.path.join(output_dir, output_filename)
                
                # Tạo file PNG tạm
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
                    temp_png_path = tmp_png.name
                    png_temp_files.append(temp_png_path)
                
                # Xử lý ảnh trong suốt
                if not remove_white_background(input_path, temp_png_path):
                    continue
                
                # Tạo file PDF tạm
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                    temp_pdf_path = tmp_pdf.name
                    pdf_temp_files.append(temp_pdf_path)
                
                # Đọc ảnh đã xử lý trong suốt
                img = cv2.imread(temp_png_path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    continue
                
                # Debug: Lưu ảnh gốc
                cv2.imwrite(os.path.join("debug_output", "original_" + image_file), img)
                
                # Tính toán kích thước mới
                height, width = img.shape[:2]
                new_width, new_height = calculate_dimensions(width, height)
                img = cv2.resize(img, (new_width, new_height))
                
                # Debug: Lưu ảnh sau resize
                cv2.imwrite(os.path.join("debug_output", "resized_" + image_file), img)
                
                # Tạo SVG
                svg = create_svg_with_transparency(img, new_width, new_height)
                
                # Lưu SVG tạm thời
                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_svg:
                    temp_svg_path = tmp_svg.name
                    svg_temp_files.append(temp_svg_path)
                    tree = ElementTree(svg)
                    tree.write(temp_svg_path, encoding='utf-8', xml_declaration=True)
                
                # Chuyển SVG sang PDF
                drawing = svg2rlg(temp_svg_path)
                renderPDF.drawToFile(drawing, temp_pdf_path)
                
                # Resize PDF xuống 144x144
                resize_pdf(temp_pdf_path, output_path)
                
                print(f"Đã chuyển đổi {image_file} thành {output_filename}")
                
            except Exception as e:
                print(f"Lỗi khi xử lý {image_file}: {str(e)}")
        
        # Xóa các file tạm sau khi hoàn thành
        print("\nĐang dọn dẹp file tạm...")
        
        # Xóa file tạm
        for temp_file in png_temp_files + svg_temp_files + pdf_temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Không thể xóa file tạm {temp_file}: {str(e)}")
        
        # Xóa thư mục debug
        debug_dir = "debug_output"
        if os.path.exists(debug_dir):
            try:
                shutil.rmtree(debug_dir)
            except Exception as e:
                print(f"Không thể xóa thư mục debug: {str(e)}")
        
        print("Đã xóa tất cả file tạm")
        
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý: {str(e)}")
    
    finally:
        # Đảm bảo xóa file tạm ngay cả khi có lỗi
        for temp_file in png_temp_files + svg_temp_files + pdf_temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        if os.path.exists(debug_dir):
            try:
                shutil.rmtree(debug_dir)
            except:
                pass

# Thư mục input và output
input_directory = "input"
output_directory = "output"

print("Bắt đầu chuyển đổi...")
image_to_pdf(input_directory, output_directory)
print("Hoàn thành")