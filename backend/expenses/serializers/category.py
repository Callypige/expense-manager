from rest_framework import serializers
from backend.expenses.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'icon', 'color', 
            'is_recurring', 'created_at'
        ]