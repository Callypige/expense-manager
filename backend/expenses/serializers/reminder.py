from rest_framework import serializers
from backend.expenses.models import Reminder

class ReminderSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    is_snoozed = serializers.ReadOnlyField()
    recurring_expense_name = serializers.CharField(source='recurring_expense.name', read_only=True)
    budget_category_name = serializers.CharField(source='budget.category.name', read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'message', 'reminder_type', 'due_date', 'frequency',
            'is_completed', 'completed_at', 'snoozed_until', 'status',
            'days_until_due', 'is_overdue', 'is_snoozed',
            'recurring_expense', 'recurring_expense_name',
            'budget', 'budget_category_name', 'created_at'
        ]
        read_only_fields = ['user', 'completed_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Reminder.objects.create(**validated_data)