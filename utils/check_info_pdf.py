import os
from PyPDF2 import PdfReader

def get_file_size(file_path):
    """
    Get file size in different units
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Dictionary containing file sizes in different units
    """
    try:
        # Get file size in bytes
        file_size = os.path.getsize(file_path)
        
        # Convert to different units
        size_info = {
            'bytes': file_size,
            'KB': round(file_size / 1024, 2),
            'MB': round(file_size / (1024 * 1024), 2),
            'GB': round(file_size / (1024 * 1024 * 1024), 2)
        }
        
        return size_info
    except FileNotFoundError:
        return {'error': 'File not found'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

def check_pdf_size(pdf_path):
    """
    Check PDF file size and other information
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing PDF size information
    """
    try:
        # Get file size information
        size_info = get_file_size(pdf_path)
        
        # Get PDF dimensions
        with open(pdf_path, 'rb') as file:
            try:
                pdf_reader = PdfReader(file)
                first_page = pdf_reader.pages[0]
                
                # Get page dimensions and convert to float
                width = float(first_page.mediabox.width)
                height = float(first_page.mediabox.height)
                
                # Convert points to inches and mm
                width_inch = round(width / 72, 2)
                height_inch = round(height / 72, 2)
                width_mm = round(width_inch * 25.4, 2)
                height_mm = round(height_inch * 25.4, 2)
                
                size_info.update({
                    'dimensions': {
                        'points': f"{width:.2f} x {height:.2f}",
                        'inches': f"{width_inch:.2f}\" x {height_inch:.2f}\"",
                        'mm': f"{width_mm:.2f}mm x {height_mm:.2f}mm"
                    },
                    'number_of_pages': len(pdf_reader.pages)
                })
                
                return size_info
            except Exception as e:
                return {'error': f'Invalid or corrupted PDF file: {str(e)}'}
                
    except FileNotFoundError:
        return {'error': 'File not found'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

# Example usage
if __name__ == "__main__":
    # Example PDF file path
    pdf_path = "output/2.pdf"
    
    # Check PDF size info
    pdf_size_info = check_pdf_size(pdf_path)
    
    # Print results
    if 'error' in pdf_size_info:
        print(f"Error: {pdf_size_info['error']}")
    else:
        print("PDF Size Information:")
        print(f"File size:")
        print(f"  - {pdf_size_info['bytes']:,} bytes")
        print(f"  - {pdf_size_info['KB']:,} KB")
        print(f"  - {pdf_size_info['MB']:,} MB")
        print(f"  - {pdf_size_info['GB']:,} GB")
        print("\nPage dimensions:")
        print(f"  - Points: {pdf_size_info['dimensions']['points']}")
        print(f"  - Inches: {pdf_size_info['dimensions']['inches']}")
        print(f"  - Millimeters: {pdf_size_info['dimensions']['mm']}")
        print(f"\nNumber of pages: {pdf_size_info['number_of_pages']}")
