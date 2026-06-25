from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # ── Trang chính ──────────────────────────────────────────────────────────
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alt'),
    path('intro/', views.intro_ptit, name='intro'),

    # ── Auth ──────────────────────────────────────────────────────────────────
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ── Sách ─────────────────────────────────────────────────────────────────
    path('book/', views.book_list, name='book'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('book/<int:book_id>/review/', views.submit_review, name='submit_review'),



    # ── Tìm kiếm ─────────────────────────────────────────────────────────────
    path('search/', views.search_page, name='search'),
    path('search-image/', views.upload_cover, name='upload_cover'),

    # ── Mượn / Trả sách ──────────────────────────────────────────────────────
    path('borrow_book/', views.list_borrowed_books, name='borrowed_books'),

    # ── Hồ sơ người dùng ─────────────────────────────────────────────────────
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # ── Quản lý Admin – Dashboard ─────────────────────────────────────────────
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard_alt'),

    # ── Quản lý Admin – Sách ─────────────────────────────────────────────────
    path('manage/books/', views.manage_books, name='manage_books'),
    path('manage/books/add/', views.add_book, name='add_book'),
    path('manage/books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('manage/books/<int:book_id>/delete/', views.delete_book, name='delete_book'),



    # ── Quản lý Admin – Người dùng ───────────────────────────────────────────
    path('manage/users/', views.manage_users, name='manage_users'),

    # ── Quản lý Admin – Yêu cầu mượn sách ───────────────────────────────────
    path('manage/borrows/', views.pending_borrows, name='pending_borrows'),
    path('manage/borrows/approve-all/', views.approve_all_borrows, name='approve_all_borrows'),
    path('manage/borrows/reject-all/', views.reject_all_borrows, name='reject_all_borrows'),
    path('manage/borrows/<int:borrow_id>/approve/', views.approve_borrow, name='approve_borrow'),
    path('manage/borrows/<int:borrow_id>/reject/', views.reject_borrow, name='reject_borrow'),
]
