from rest_framework import serializers
from .models import Todo, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['owner'] # <-- Đã thêm


# Class tùy chỉnh này sẽ "dịch" qua lại giữa String (trong DB) và Array (trong JSON)
class TagsField(serializers.Field):
    """
    Trường tùy chỉnh để xử lý tags.
    DB: "api, backend" (String)
    JSON: ["api", "backend"] (Array)
    """
    
    # Dịch từ Database (String) sang JSON (Array)
    def to_representation(self, value):
        if not value:
            return []
        return [tag.strip() for tag in value.split(',') if tag.strip()]

    # Dịch từ JSON (Array) sang Database (String)
    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Tags phải là một mảng (array).")
        return ", ".join(tag.strip() for tag in data if tag.strip())


class TodoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    # Ghi đè (override) trường 'tags' để dùng class 'TagsField'
    tags = TagsField(required=False) 

    class Meta:
        model = Todo
        # Khai báo fields thủ công
        fields = [
            'id', 'title', 'description', 'category', 'priority',
            'created_at', 'due_at', 'remind_at', 'completed',
            'tags', 'category_name',
            'daily_reminder_time',
            'owner'
        ]
        # Thêm 'owner' vào read_only_fields
        read_only_fields = ['owner', 'created_at', 'category_name']