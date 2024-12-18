import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

def trace_bitmap_with_inkscape(input_path, output_path):
    """
    Dùng Inkscape để chuyển đổi ảnh bitmap thành PDF, áp dụng Trace Bitmap và Union.
    Chạy ở chế độ không giao diện (headless).
    """
    command = [
        "inkscape",
        "--batch-process",  # Chế độ xử lý không giao diện
        "--actions=EditSelectAll;ObjectTraceBitmap;PathUnion;FileSave;FileClose",  # Trace Bitmap và Union
        "--export-type=pdf",  # Xuất ra PDF
        input_path,
        "-o", output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Đã tạo PDF hợp nhất: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi xử lý {input_path}: {e.stderr.strip()}")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy Inkscape. Vui lòng cài đặt Inkscape và thêm vào PATH.")

def batch_trace_bitmap(input_dir, output_dir):
    """
    Xử lý hàng loạt ảnh trong thư mục input và lưu PDF vào thư mục output.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with ThreadPoolExecutor() as executor:
        futures = []
        for file in os.listdir(input_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):  # Hỗ trợ các định dạng ảnh
                input_path = os.path.join(input_dir, file)
                output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.pdf")
                print(f"Đang xử lý: {file}")
                futures.append(executor.submit(trace_bitmap_with_inkscape, input_path, output_path))

        for future in as_completed(futures):
            try:
                future.result()  # Get the result to raise any exceptions
            except Exception as e:
                print(f"Lỗi khi xử lý: {e}")

if __name__ == "__main__":
    input_directory = "input"   # Thư mục chứa các ảnh bitmap đầu vào
    output_directory = "output" # Thư mục để lưu các file PDF kết quả

    print("Bắt đầu chuyển đổi ảnh bitmap sang PDF với Trace Bitmap và Union...")
    batch_trace_bitmap(input_directory, output_directory)
    print("Quá trình hoàn tất! Kết quả đã được lưu vào thư mục output.")
