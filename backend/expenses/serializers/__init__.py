# ================================================================
# backend/expenses/serializers/__init__.py
# ================================================================

"""
Expense Management Serializers

This module centralizes all serializer imports for easy access.
Import pattern: from .serializers import CategorySerializer
"""

# Import all serializers from their respective files
from .category import CategorySerializer
from .recurring_expense import RecurringExpenseSerializer
from .transaction import TransactionSerializer
from .budget import BudgetSerializer
from .reminder import ReminderSerializer
from .user import UserSerializer

# Define what gets imported when using "from .serializers import *"
__all__ = [
    'CategorySerializer',
    'RecurringExpenseSerializer', 
    'TransactionSerializer',
    'BudgetSerializer',
    'ReminderSerializer',
    'UserSerializer',
]