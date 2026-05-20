import django, os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
sys.stdout.reconfigure(encoding='utf-8')
django.setup()
from myapp.models import Book

books = Book.objects.all()
for b in books:
    print(f'id={b.id} | image={repr(b.image.name)} | title={b.title}')
