from celery import shared_task
from django.utils import timezone
from datetime import datetime, time

@shared_task
def check_voting_end_dates():
    """
    Check rules that have reached their voting end date/time and close their voting.
    """
    from .models import Rule
    
    now = timezone.now()
    today = now.date()
    current_time = now.time()
    
    # Get rules that have reached their end date/time
    rules_to_close = Rule.objects.filter(
        voting_closed=False,
        voting_end_date__lte=today
    ).exclude(voting_end_date=None)
    
    for rule in rules_to_close:
        # If the rule has a specific end time, check if it has been reached
        if rule.voting_end_time:
            if rule.voting_end_date == today and rule.voting_end_time <= current_time:
                rule.voting_closed = True
                rule.save()
        else:
            # If no specific time is set, close voting at the end of the day
            rule.voting_closed = True
            rule.save() 