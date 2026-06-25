from django import forms
from django.contrib.auth.models import User
from .models import Book, BookReview, CATEGORY_CHOICES


class BookCoverForm(forms.Form):
    image = forms.ImageField()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Tên',
            'last_name': 'Họ',
            'email': 'Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'category', 'description', 'uri', 'image', 'pdf_file', 'quantity']
        labels = {
            'title': 'Tên sách',
            'author': 'Tác giả',
            'publisher': 'Nhà xuất bản',
            'category': 'Thể loại',
            'description': 'Mô tả',
            'uri': 'Link đọc online (URL)',
            'image': 'Ảnh bìa',
            'pdf_file': 'File sách (PDF)',
            'quantity': 'Số lượng',
        }
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên sách'}),
            'author':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên tác giả'}),
            'publisher':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhà xuất bản'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả ngắn về sách...'}),
            'uri':         forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'quantity':    forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }





class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['rating', 'comment']
        labels = {
            'rating':  'Đánh giá',
            'comment': 'Nhận xét',
        }
        widgets = {
            'rating':  forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Chia sẻ cảm nhận của bạn về cuốn sách này...'
            }),
        }
