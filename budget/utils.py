
# # budget/utils.py
# from decimal import Decimal
# from django.contrib import messages
# from django.utils import timezone
# from django.conf import settings
# from django.core.mail import send_mail
# from .models import Budget, BudgetCategory

# def check_budget_warnings(request, expense):
#     user = request.user
#     category_name = expense.category
#     today = timezone.now().date()

#     active_budgets = Budget.objects.filter(
#         user=user,
#         start_date__lte=today,
#         end_date__gte=today,
#         categories__category=category_name
#     ).distinct()

#     for budget in active_budgets:
#         cat_obj = budget.categories.filter(category=category_name).first()
#         if not cat_obj:
#             continue  

#         spent = cat_obj.spent()
#         limit = cat_obj.limit_amount()  

#         if spent > limit:
#             messages.warning(
#                 request,
#                 f"⚠️ You have exceeded the limit for category '{category_name}' "
#                 f"in budget '{budget.name}'. Spent: {spent}, Limit: {limit}"
#             )

#         total_spent = sum(c.spent() for c in budget.categories.all())
#         total_limit = Decimal(budget.total_amount)

#         if total_spent > total_limit:
#             messages.error(
#                 request,
#                 f"🚨 Your total spending ({total_spent}) exceeded the budget '{budget.name}' limit ({total_limit})!"
#             )

#         try:
#             expense_amt = Decimal(getattr(expense, "amount", 0) or 0)

#             prev_total_spent = (total_spent - expense_amt)
#             if prev_total_spent < Decimal('0'):
#                 prev_total_spent = Decimal('0')

#             crossed = (prev_total_spent <= total_limit) and (total_spent > total_limit)

#             if crossed:
#                 user_email = getattr(user, "email", None)
#                 if user_email:
#                     subject = f"Personal Finance Manager – Budget '{budget.name}' Exceeded"
#                     message = (
#                         f"Hello {user.get_full_name() or user.username},\n\n"
#                         f"This is an alert from your Personal Finance Manager app.\n\n"
#                         f"Your budget \"{budget.name}\" has now exceeded its 100% spending limit.\n\n"
#                         f"• Budget Limit: {total_limit}\n"
#                         f"• Previous Total: {prev_total_spent}\n"
#                         f"• New Expense: {expense_amt} (Category: {category_name})\n"
#                         f"• Current Total: {total_spent}\n\n"
#                         f"We recommend reviewing your recent expenses to stay on track.\n\n"
#                         f"— Personal Finance Manager"
#                     )
#                     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
#                     send_mail(subject, message, from_email, [user_email], fail_silently=False)
#                 else:
#                     messages.info(request, "Budget exceeded but no user email configured for alert.")
#         except Exception:
#             messages.info(request, "Budget exceeded — failed to send email alert (check email settings).")
import threading
from decimal import Decimal
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import Budget, BudgetCategory

# 1. Add this Helper Class to send emails in the background
class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject, 
                self.message, 
                self.from_email, 
                self.recipient_list, 
                fail_silently=False
            )
            print(f"✅ Email sent successfully to {self.recipient_list}")
        except Exception as e:
            # This prints the REAL error to your server logs
            print(f"❌ EMAIL FAILURE LOG: {e}")

def check_budget_warnings(request, expense):
    user = request.user
    category_name = expense.category
    today = timezone.now().date()

    active_budgets = Budget.objects.filter(
        user=user,
        start_date__lte=today,
        end_date__gte=today,
        categories__category=category_name
    ).distinct()

    for budget in active_budgets:
        cat_obj = budget.categories.filter(category=category_name).first()
        if not cat_obj:
            continue  

        spent = cat_obj.spent()
        limit = cat_obj.limit_amount()  

        if spent > limit:
            messages.warning(
                request,
                f"⚠️ You have exceeded the limit for category '{category_name}' "
                f"in budget '{budget.name}'. Spent: {spent}, Limit: {limit}"
            )

        total_spent = sum(c.spent() for c in budget.categories.all())
        total_limit = Decimal(budget.total_amount)

        if total_spent > total_limit:
            messages.error(
                request,
                f"🚨 Your total spending ({total_spent}) exceeded the budget '{budget.name}' limit ({total_limit})!"
            )

        # 2. Logic to detect if we JUST crossed the limit
        try:
            expense_amt = Decimal(getattr(expense, "amount", 0) or 0)
            prev_total_spent = (total_spent - expense_amt)
            if prev_total_spent < Decimal('0'):
                prev_total_spent = Decimal('0')

            crossed = (prev_total_spent <= total_limit) and (total_spent > total_limit)

            if crossed:
                user_email = getattr(user, "email", None)
                if user_email:
                    subject = f"Personal Finance Manager – Budget '{budget.name}' Exceeded"
                    message = (
                        f"Hello {user.get_full_name() or user.username},\n\n"
                        f"Your budget \"{budget.name}\" has now exceeded its limit.\n\n"
                        f"• Budget Limit: {total_limit}\n"
                        f"• Current Total: {total_spent}\n\n"
                        f"— Personal Finance Manager"
                    )
                    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
                    
                    # 3. USE THE THREAD (Non-blocking)
                    # This prevents the "Failed" popup from showing up in the UI
                    EmailThread(subject, message, from_email, [user_email]).start()
                    
                else:
                    messages.info(request, "Budget exceeded but no user email configured.")
                    
        except Exception as e:
            # flush=True forces the log to appear instantly
            print(f"❌ EMAIL FAILURE LOG: {e}", flush=True)
