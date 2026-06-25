from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator

CATEGORY_CHOICES = [
    ('cong_nghe', 'Công nghệ - CNTT'),
    ('van_hoc', 'Văn học'),
    ('kinh_te', 'Kinh tế'),
    ('ngoai_ngu', 'Ngoại ngữ'),
    ('khoa_hoc', 'Khoa học tự nhiên'),
    ('xa_hoi', 'Khoa học xã hội'),
    ('giao_duc', 'Giáo dục - Tâm lý'),
    ('ky_thuat', 'Kỹ thuật - Công nghệ'),
    ('khac', 'Khác'),
]

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='khac',
        verbose_name='Thể loại'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    uri = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    pdf_file = models.FileField(upload_to='book_pdfs/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    def get_category_display_name(self):
        return dict(CATEGORY_CHOICES).get(self.category, 'Khác')

    def average_rating(self):
        reviews = self.bookreview_set.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def review_count(self):
        return self.bookreview_set.count()



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


class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']


BORROW_STATUS_CHOICES = [
    ('pending',  'Chờ xác nhận'),
    ('approved', 'Đã duyệt'),
    ('rejected', 'Từ chối'),
]

class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=BORROW_STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @property
    def estimated_fee_formatted(self):
        if self.expected_return_date and self.borrowed_at:
            days = (self.expected_return_date - self.borrowed_at.date()).days
            if days <= 0:
                days = 0
            fee = days * 3000
            return f"{fee:,}".replace(",", ".")
        return "0"

    def is_borrowed(self):
        return self.returned_at is None and self.status == 'approved'

    def is_overdue(self):
        from django.utils import timezone
        if self.expected_return_date and self.returned_at is None and self.status == 'approved':
            return timezone.now().date() > self.expected_return_date
        return False



class BookReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người đánh giá')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Sách')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Số sao'
    )
    comment = models.TextField(blank=True, verbose_name='Nhận xét')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # Mỗi user chỉ đánh giá 1 lần cho mỗi sách
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username} – {self.book.title} ({self.rating}★)"
