from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    uri = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)  
    pdf_file = models.FileField(upload_to='book_pdfs/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.title
    
class Giaotrinh(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    uri = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)  
    def __str__(self):
        return self.title


class CreateRegister(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, label="Họ và Tên")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        user.last_name = parts[0]
        user.first_name = parts[1] if len(parts) > 1 else ''
        if commit:
            user.save()
        return user
        
class  UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)  

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def is_borrowed(self):
   
        return self.returned_at is None
    
