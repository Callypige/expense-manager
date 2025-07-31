from django.contrib import admin

from expenses.models import Budget, Category, RecurringExpense, Reminder, Transaction

# Register your models here.
admin.site.register(Category)
admin.site.register(RecurringExpense)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(Reminder)