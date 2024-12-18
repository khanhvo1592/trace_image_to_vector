

## Hướng dẫn sử dụng trace_image.py
HELLO EM THẤY CHƯA
### Mô tả
Chương trình này chuyển đổi các file hình ảnh PNG thành file PDF bằng cách sử dụng OpenCV để xử lý hình ảnh và tạo SVG từ các contours.

1 Tạo môi trường python
Tạo trên Mac:   
```bash
python3 -m venv venv
source venv/bin/activate
```

2 Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

3 Chạy chương trình
```bash
python trace_image.py
```

# LƯU Ý:
- Coppy các hình ảnh vào folder input
- Chương trình sẽ tạo ra các file pdf đã xử lý răng cưa và tăng chất lượng trong folder output
- Các file pdf đã xử lý răng cưa và tăng chất lượng sẽ được đặt tên theo đúng thứ tự của các file hình ảnh trong folder input


--
inkscape --actions="EditSelectAll;FileImportBitmap"
