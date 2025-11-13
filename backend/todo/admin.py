from django.contrib import admin
from .models import Category, Todo

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'owner')
    list_filter = ('owner',)
    search_fields = ('name',)

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'owner',
        'priority',
        'completed',    # <-- Thay cho 'status'
        'category',
        'due_at',       # <-- Thay cho 'deadline'
        'daily_reminder_time', # <-- Thêm
    )
    list_filter = (
        'priority',
        'completed',
        'category',
        'due_at',
        'owner',
    )
    search_fields = ('title','description', 'tags', 'owner__username')