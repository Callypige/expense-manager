from backend.expenses.models import Transaction
from rest_framework import serializers

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    recurring_expense_name = serializers.CharField(source='recurring_expense.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'transaction_type', 'date',
            'payment_method', 'was_impulsive', 'notes', 'tags',
            'category', 'category_name', 'category_icon', 'category_color',
            'recurring_expense', 'recurring_expense_name', 'created_at'
        ]
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Transaction.objects.create(**validated_data)