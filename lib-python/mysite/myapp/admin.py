from django.contrib import admin
from .models import Book, Giaotrinh, UserHistory, BorrowRecord

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'quantity', 'uri', 'has_pdf')
    search_fields = ('title', 'author', 'publisher')
    list_filter = ('author', 'publisher')

    @admin.display(boolean=True, description='Có PDF?')
    def has_pdf(self, obj):
        return bool(obj.pdf_file)

@admin.register(Giaotrinh)
class GiaotrinhAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uri')
    search_fields = ('title', 'author')

@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'viewed_at')
    list_filter = ('viewed_at', 'user')

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_at', 'expected_return_date', 'returned_at', 'is_borrowed')
    list_filter = ('borrowed_at', 'expected_return_date', 'returned_at', 'user')
    search_fields = ('user__username', 'book__title', 'note')
