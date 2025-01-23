import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.timezone import now

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = now().timestamp()

            if last_activity:
                inactive_time = current_time - last_activity
                if inactive_time > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    request.session.flush()
                    return redirect('login')  # Перенаправление на страницу входа

            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response
