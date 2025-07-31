from rest_framework import serializers
from backend.expenses.models import Budget
from backend.expenses.models import Reminder

class BudgetSerializer(serializers.ModelSerializer):
    spent_amount = serializers.ReadOnlyField()
    remaining_budget = serializers.ReadOnlyField()
    percentage_used = serializers.ReadOnlyField()
    should_alert = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_icon', 'category_color',
            'month', 'year', 'budget_amount', 'alert_threshold',
            'spent_amount', 'remaining_budget', 'percentage_used', 
            'should_alert', 'created_at'
        ]
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        budget = Budget.objects.create(**validated_data)
        
        # Check if we need to create a budget alert
        if budget.should_alert:
            Reminder.create_budget_reminder(budget)
            
        return budget
