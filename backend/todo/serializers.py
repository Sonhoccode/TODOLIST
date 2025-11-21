from rest_framework import serializers
from .models import Todo, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['owner']
        
    def validate_name(self, value):
        user = self.context['request'].user
        if Category.objects.filter(owner=user, name=value).exists():
            raise serializers.ValidationError("Danh mục đã tồn tại.")
        return value


class TagsField(serializers.Field):
    def to_representation(self, value):
        if not value:
            return []
        return [tag.strip() for tag in value.split(',') if tag.strip()]

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Tags phải là một mảng.")
        return ", ".join(tag.strip() for tag in data if tag.strip())


class TodoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagsField(required=False)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'category', 'priority',
            'created_at', 'due_at', 'remind_at', 'completed',
            'tags', 'category_name', 'daily_reminder_time', 'owner',
            'planned_start_at', 'estimated_duration_min', 'completed_at'
        ]
        read_only_fields = ['owner', 'created_at', 'category_name', 'completed_at']