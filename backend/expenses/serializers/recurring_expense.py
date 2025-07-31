from backend.expenses.models import RecurringExpense
from backend.expenses.models import Reminder
from rest_framework import serializers

class RecurringExpenseSerializer(serializers.ModelSerializer):
    monthly_cost = serializers.ReadOnlyField()
    days_until_billing = serializers.ReadOnlyField()
    needs_reminder = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    class Meta:
        model = RecurringExpense
        fields = [
            'id', 'name', 'description', 'amount', 'billing_cycle',
            'next_billing_date', 'payment_method', 'website_url',
            'is_active', 'reminder_days', 'monthly_cost', 'days_until_billing',
            'needs_reminder', 'is_overdue', 'category', 'category_name',
            'category_icon', 'category_color', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        recurring_expense = RecurringExpense.objects.create(**validated_data)
        
        # Auto-create reminder for new subscription
        from .models import Reminder
        Reminder.create_bill_reminder(recurring_expense)
        
        return recurring_expense
    
    def update(self, instance, validated_data):
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update reminder if billing date changed
        if 'next_billing_date' in validated_data or 'reminder_days' in validated_data:
            # Delete old reminder
            Reminder.objects.filter(
                recurring_expense=instance,
                reminder_type='bill_due',
                is_completed=False
            ).delete()
            
            # Create new reminder
            Reminder.create_bill_reminder(instance)
        
        return instance