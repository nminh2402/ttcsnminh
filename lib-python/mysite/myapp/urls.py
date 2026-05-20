from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_page, name='search'),
    path('book/', views.book_list, name='book'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('intro/', views.intro_ptit, name='intro'),
    path('home/', views.home, name='home'),
    path('giaotrinh/<int:giaotrinh_id>/', views.giaotrinh_detail, name='giaotrinh_detail'),
    path('search-image/', views.upload_cover, name='upload_cover'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('borrow_book/', views.list_borrowed_books, name='borrowed_books'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('prof/', views.profile_view, name='profile'),

    # ── Quản lý sách (Admin CRUD) ──────────────────────────────────────────
    path('manage/books/', views.manage_books, name='manage_books'),
    path('manage/books/add/', views.add_book, name='add_book'),
    path('manage/books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('manage/books/<int:book_id>/delete/', views.delete_book, name='delete_book'),



] 

