from django import forms
from django.contrib.auth.models import User
from .models import Book

class BookCoverForm(forms.Form):
    image = forms.ImageField()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'uri', 'image', 'pdf_file', 'quantity']
        labels = {
            'title': 'Tên sách',
            'author': 'Tác giả',
            'publisher': 'Nhà xuất bản',
            'uri': 'Link đọc online (URL)',
            'image': 'Ảnh bìa',
            'pdf_file': 'File PDF',
            'quantity': 'Số lượng',
        }
        widgets = {
            'title':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sách'}),
            'author':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên tác giả'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhà xuất bản'}),
            'uri':       forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'quantity':  forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
