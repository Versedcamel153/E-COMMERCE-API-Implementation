# middleware.py

from django.utils.deprecation import MiddlewareMixin
import requests

class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get('access_token')
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            user_details_response = requests.get('http://127.0.0.1:8000/api/users/me/', headers=headers)
            if user_details_response.status_code == 200:
                request.user_details = user_details_response.json()
            else:
                request.user_details = None
        else:
            request.user_details = None
            
class TokenExpiryMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.session.get('access_token')
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            baseURL = 'http://127.0.0.1:8000/api'
            response = requests.get(f"{baseURL}/users/me/", headers=headers)
            if response.status_code == 401:  # Unauthorized, token might be expired
                request.session.flush()
                from django.contrib import messages
                from django.shortcuts import redirect
                messages.error(request, 'Session expired. Please log in again.')
                return redirect('login')
