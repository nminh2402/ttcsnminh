from django.utils import timezone
from .models import BorrowRecord

class ExpireBorrowsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Auto-delete expired borrow records before handling the request
        try:
            today = timezone.now().date()
            BorrowRecord.objects.filter(
                expected_return_date__lt=today,
                status__in=['approved', 'pending']
            ).delete()
        except Exception:
            pass

        response = self.get_response(request)
        return response
