# backend/expenses/models.py - Simplified models with TDAH reminders focus

from django.db import models 
from django.contrib.auth.models import User 
from django.utils import timezone 
from decimal import Decimal
from datetime import timedelta

class Category(models.Model):
    """Category of expense (food, subscription...)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='💰')
    color = models.CharField(max_length=7, default='#007bff')
    is_recurring = models.BooleanField(default=False)  # Netflix, Spotify...
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name
    
class RecurringExpense(models.Model):
    """Recurring expense (Netflix, Spotify, etc.)"""
    BILLING_CYCLES = [
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
        ('weekly', 'Hebdomadaire'),
        ('quarterly', 'Trimestriel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_expenses')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Basic information
    name = models.CharField(max_length=200)  # "Netflix Premium"
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    next_billing_date = models.DateField()
    payment_method = models.CharField(max_length=50, blank=True)

    # Practical info
    website_url = models.URLField(blank=True)
    
    # Management and reminders
    is_active = models.BooleanField(default=True)
    reminder_days = models.IntegerField(default=3, help_text="Reminder X days before billing")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_billing_date']

    def __str__(self):
        return f"{self.name} - {self.amount}€/{self.billing_cycle}"

    @property
    def monthly_cost(self):
        """Equivalent monthly cost"""
        if self.billing_cycle == 'monthly':
            return self.amount
        elif self.billing_cycle == 'yearly':
            return self.amount / 12
        elif self.billing_cycle == 'weekly':
            return self.amount * 4.33
        elif self.billing_cycle == 'quarterly':
            return self.amount / 3
        return self.amount

    @property
    def days_until_billing(self):
        """Number of days until next bill"""
        today = timezone.now().date()
        return (self.next_billing_date - today).days

    @property
    def needs_reminder(self):
        """Should we send a reminder?"""
        return self.days_until_billing <= self.reminder_days and self.days_until_billing >= 0

    @property
    def is_overdue(self):
        """Bill is overdue"""
        return self.days_until_billing < 0

class Transaction(models.Model):
    """Ponctual expense or income"""
    TRANSACTION_TYPES = [
        ('expense', 'Dépense'),
        ('income', 'Revenu'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    recurring_expense = models.ForeignKey(
        RecurringExpense,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="If linked to a subscription"
    )

    # Basic information
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=True)

    # Simple context
    was_impulsive = models.BooleanField(default=False, help_text="Impulsive purchase?")

    # Metadata
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}€"

class Budget(models.Model):
    """Budget for a specific category and month/year"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Simple reminder functionality
    alert_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.80'),
        help_text="Alert at X% of budget (0.80 = 80%)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['-year', '-month']
    
    @property
    def spent_amount(self):
        """Calculate total spent amount for this budget period."""
        from django.db.models import Sum 
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            date__month=self.month,
            date__year=self.year
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    @property
    def remaining_budget(self):
        return self.budget_amount - self.spent_amount
    
    @property
    def percentage_used(self):
        """Percentage of budget used"""
        if self.budget_amount == 0:
            return 0
        return float(self.spent_amount / self.budget_amount * 100)
    
    @property
    def should_alert(self):
        """Should we alert the user?"""
        return self.percentage_used >= float(self.alert_threshold * 100)
    
    def __str__(self):
        return f"{self.category.name} - {self.budget_amount}€ ({self.month}/{self.year})"

# ================================================================
# MAIN MODEL: REMINDERS FOR TDAH
# ================================================================

class Reminder(models.Model):
    """Reminder system for TDAH - MAIN FEATURE"""
    REMINDER_TYPES = [
        ('bill_due', 'Bill due'),
        ('budget_check', 'Budget check'),
        ('weekly_review', 'Weekly review'),
        ('custom', 'Custom'),
    ]

    FREQUENCIES = [
        ('once', 'Once'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    
    # Reminder content
    title = models.CharField(max_length=200)
    message = models.TextField()
    reminder_type = models.CharField(max_length=30, choices=REMINDER_TYPES)
    
    # Timing
    due_date = models.DateTimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCIES, default='once')
    
    # Optional links
    recurring_expense = models.ForeignKey(RecurringExpense, on_delete=models.CASCADE, null=True, blank=True)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    snoozed_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.due_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def is_overdue(self):
        """Reminder is overdue"""
        return timezone.now() > self.due_date and not self.is_completed

    @property
    def is_snoozed(self):
        """Reminder is temporarily postponed"""
        return self.snoozed_until and timezone.now() < self.snoozed_until

    @property
    def status(self):
        """Visual status of reminder"""
        if self.is_completed:
            return "✅ Done"
        elif self.is_snoozed:
            return "😴 Snoozed"
        elif self.is_overdue:
            return "🔴 Overdue"
        elif self.days_until_due <= 1:
            return "🟡 Urgent"
        else:
            return "⏰ Upcoming"

    @property
    def days_until_due(self):
        """Days until due date"""
        return (self.due_date.date() - timezone.now().date()).days

    def snooze(self, hours=2):
        """Postpone reminder by X hours (very useful TDAH function)"""
        self.snoozed_until = timezone.now() + timedelta(hours=hours)
        self.save()

    def mark_completed(self):
        """Mark as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

        # If recurring, create next reminder
        if self.frequency != 'once':
            self.create_next_reminder()

    def create_next_reminder(self):
        """Create next recurring reminder"""
        if self.frequency == 'weekly':
            next_due = self.due_date + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            next_due = self.due_date + timedelta(days=30)
        else:
            return

        Reminder.objects.create(
            user=self.user,
            title=self.title,
            message=self.message,
            reminder_type=self.reminder_type,
            due_date=next_due,
            frequency=self.frequency,
            recurring_expense=self.recurring_expense,
            budget=self.budget,
        )

    @classmethod
    def create_bill_reminder(cls, recurring_expense):
        """Automatically create reminder for a bill"""
        reminder_date = recurring_expense.next_billing_date - timedelta(days=recurring_expense.reminder_days)
        
        return cls.objects.create(
            user=recurring_expense.user,
            title=f"Bill {recurring_expense.name}",
            message=f"Bill {recurring_expense.name} ({recurring_expense.amount}€) due on {recurring_expense.next_billing_date.strftime('%d/%m/%Y')}",
            reminder_type='bill_due',
            due_date=timezone.datetime.combine(reminder_date, timezone.datetime.min.time().replace(hour=9)),
            recurring_expense=recurring_expense,
        )

    @classmethod
    def create_budget_reminder(cls, budget):
        """Create reminder when budget reaches threshold"""
        if budget.should_alert:
            return cls.objects.create(
                user=budget.user,
                title=f"Budget {budget.category.name} at {budget.percentage_used:.0f}%",
                message=f"You've used {budget.percentage_used:.0f}% of your {budget.category.name} budget this month.",
                reminder_type='budget_check',
                due_date=timezone.now(),
                budget=budget,
            )