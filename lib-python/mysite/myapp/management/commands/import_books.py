import sys
import io
import pandas as pd
import requests
from django.core.management.base import BaseCommand
from django.core.files import File
from io import BytesIO
from myapp.models import Book

class Command(BaseCommand):
    help = 'Import books from Excel into Django database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, **kwargs):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        file_path = kwargs['file_path']
        
        try:
            df = pd.read_excel(file_path)
            
            # Chuẩn hóa tên cột
            df.columns = df.columns.str.strip().str.title()
            
            for index, row in df.iterrows():
                try:
                    book = Book(
                        title=row.get('Title', '').strip(),
                        author=row.get('Author', '').strip(),
                        publisher=row.get('Publisher', '').strip(),
                        uri=row.get('Url', '').strip(),
                    )
                    
                    # Xử lý ảnh từ URL
                    image_url = row.get('Image', '').strip()  # Giả sử cột chứa URL ảnh là 'Image'
                    if image_url and image_url.startswith(('http://', 'https://')):
                        try:
                            response = requests.get(image_url, timeout=10)
                            response.raise_for_status()  # Kiểm tra lỗi HTTP
                            
                            # Lấy tên file từ URL (hoặc đặt tên theo title)
                            image_name = image_url.split('/')[-1] or f"book_{book.title}.jpg"
                            
                            # Lưu ảnh vào ImageField
                            book.image.save(
                                image_name,
                                File(BytesIO(response.content)),
                                save=False
                            )
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(
                                f"Không thể tải ảnh từ {image_url} cho sách {book.title}: {str(e)}"
                            ))
                    
                    book.save()
                    self.stdout.write(self.style.SUCCESS(f"[OK] Imported: {book.title}"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"[ERROR] Row {index+2}: {str(e)}"))
                    
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("[ERROR] Excel file not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] System error: {str(e)}"))
        finally:
            self.stdout.write(self.style.SUCCESS("[DONE] Import finished."))