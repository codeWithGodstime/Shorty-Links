import time
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is anonymous
        if not request.user.is_authenticated:
            # Get or initialize the attempt count in the session
            attempts = request.session.get('attempts', 0)
            # print(f'CALLED ATTEMPTS {attempts}')
            # print(request.session.get('session_key'))
            session_key = request.session.session_key

            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            # print(session_key)

            # Set the rate limit (e.g., 5 attempts per hour)
            max_attempts = 5

            # Check if the user has exceeded the rate limit
            if attempts >= max_attempts:
                return HttpResponse("Limit Exceeded. Try again later.", status=429)
        if request.path == reverse('index') and request.user.is_authenticated:
            return redirect('dashboard')

        response = self.get_response(request)
        return response
