from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
import requests
import os
from .models import User
# Create your views here.

baseURL = os.getenv('BASE_URL')



# token_manager.py
token = None
#API_KEY = "KAiepDY3.MCpEp2Kr0QZ8NCUm9ittP4xJuVQBCnpp"
API_KEY = os.getenv('API-KEY')

def fetch_token():
    global token
    token_endpoint = f"{baseURL}/users/token/"
    login_data = {
        'email': 'seidufarid206@gmail.com',
        'password': '919120$'
    }
    response = requests.post(token_endpoint, data=login_data)
    response_data = response.json()
    token = response_data.get('access')
    return token

def get_token():
    if not token:
        return fetch_token()
    return token

def get_cart_data(request):
    headers = {'API-KEY': API_KEY}
    params = {'user_id': str(request.user.id)}
    response = requests.get(f"{baseURL}/cart/", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()  # or return just the data you need
    return None

def get_user_details(token, user_id):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{baseURL}/users/{user_id}/', headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def product_list(request):
    # Fetching products
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/", headers=headers)
    data = response.json()
    print(data)
    products = data['results']
    
    # Get cart data if user is logged in
    
    cart = get_cart_data(request)  # Using the helper method to fetch cart data
    
    return render(request, 'webapp/product_list.html', {'products': products, 'cart': cart})

def product_detail(request, slug):
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/{slug}/", headers=headers)
    if response.status_code == 200 and response.json():
        product = response.json()
    else:
        # Handle the case where the product is not found
        return render(request, 'webapp/error.html', {'message': 'Product not found'})
    
    response = requests.get(f"{baseURL}/products/{slug}/", headers=headers)
    product = response.json()
    
    
    cart = get_cart_data(request)  # Using the helper method to fetch cart data

    return render(request, 'webapp/product_details.html', {'product': product, 'cart': cart})

@login_required(login_url='login')
def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    
    headers = {'API-KEY': API_KEY}
    params = {'user_id': str(request.user.id)}
    response = requests.get(f"{baseURL}/cart/", headers=headers, params=params)
    # Check if the request was successful (HTTP status 200)
    if response.status_code == 200:
        print(f'User: {request.user.id}')
        try:
            cart_data = response.json()  # Try to parse JSON
        except ValueError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Response content: {response.text}")
            cart_data = {}
    else:
        print(f"Failed to fetch cart: {response.status_code}")
        cart_data = {}
        print(f'User: {request.user.id}')


    return render(request, 'webapp/cart.html', {'cart': cart_data})
    #return JsonResponse(cart_data, safe=False)

@login_required(login_url='login')
def add_to_cart(request, slug):
    # Check if user details are present; redirect to login if not
    if not request.user.is_authenticated:
        return redirect('login')
    
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/{slug}/", headers=headers)
    if response.status_code == 200 and response.json():
        product = response.json()
        product_id = product['id']
    else:
        # Handle the case where the product is not found
        return render(request, 'webapp/error.html', {'message': 'Product not found'})

    # Ensure CSRF token is present
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        user_id = str(request.user.id)
        

        payload = {'user_id': user_id, 'product': product_id, 'quantity': quantity}
        response = requests.post(f"{baseURL}/cart/add/", headers=headers, json=payload, params=params)

        if response.status_code == 201:
            messages.success(request, 'Product added to cart')
            return redirect('webapp-cart')
        else:
            messages.error(request, 'Failed to add to cart')
            print(f"Failed to add to cart: {response.content}")
            return render(request, 'webapp/error.html', {'message': response.json()})
    else:
        messages.error(request, 'Invalid request method')
        return redirect('webapp-product-details', slug=slug)
        
def decrease_cart_item(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    headers = {'API-KEY': API_KEY}
    response = requests.patch(f"{baseURL}/cart/{product_id}/decrease/", headers=headers)

    if response.status_code == 200 or 204:
        print("OK")
        messages.success(request, 'Cart updated!')
        return redirect('webapp-cart')
    else:
        print(f"Failed to decrease item quantity: {response.content}")
        messages.error(request, 'Failed to update cart.')
        return render(request, 'webapp/error.html', {'message': {response.content}})
    
def increase_cart_item(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    headers = {'API-KEY': API_KEY}
    response = requests.patch(f"{baseURL}/cart/{product_id}/increase/", headers=headers)

    if response.status_code == 200:
        print('OK')
        messages.success(request, 'Cart updated!')
        return redirect('webapp-cart')
    else:
        print(f"Failed to increase item quanitity: {response.content}")
        messages.error(request, 'Failed to update cart.')
        return render(request, 'webapp/error.html', {'message': response.content})

def delete_cart_item(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    headers = {'API-KEY': API_KEY}
    response = requests.delete(f"{baseURL}/cart/{product_id}/remove/", headers=headers)

    if response.status_code == 204:
        print("Deleted cart item")
        return redirect('webapp-cart')
    else:
        print(f"Failed to delete item: {response.content}")
        return render(request, 'webapp/error.html', {'message': {response.content}})

def login(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        user = authenticate(request, email=email, password=password)
        print(user)
        if user:
            auth_login(request, user)
            return redirect('webapp')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'webapp/login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.create_user(email=email, username=username, password=password)
        user.save()
        return redirect('login')

    return render(request, 'webapp/register.html')

def logout(request):
    request.session.flush()
    auth_logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('login')

def review_list(request, slug):

    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/{slug}/reviews/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        reviews = data.get('results', [])
    else:
        reviews = []
    return render(request, 'webapp/review_list.html', {'reviews': reviews})
    #return JsonResponse(reviews, safe=False)

def submit_review(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/{slug}/", headers=headers)
    if response.status_code == 200 and response.json():
        product = response.json()
        product_id = product['id']
    else:
        # Handle the case where the product is not found
        return render(request, 'webapp/error.html', {'message': 'Product not found'})


    if request.method == 'POST':
        user_id = str(request.user.id)
        username = request.user.username
        print(username)
        rating = request.POST.get('rating-2')
        comment = request.POST.get('comment')
        payload = {
                    "user_id": user_id,
                    "username": username,
                    "product": product_id,
                    "rating": rating,
                    "comment": comment,
                }
        print(payload)
        response = requests.post(f"{baseURL}/products/{slug}/reviews/create/", json=payload, headers=headers)
        product = response.json()
        print(product)
        if response.status_code == 201:
            messages.success(request, "Review created successfully!")
            return redirect('webapp-product-details', slug=slug)
        else:
            print(f"Failed to submit review: {response.content}")
            messages.error(request, "Error submitting review.")
            return redirect('submit-review', slug)
        
    else:
        return render(request, 'webapp/review.html', {'product': product})
    
def create_order(request):
    if not request.user.is_authenticated:
        return redirect('login')

    params = {'user_id': str(request.user.id)}
    headers = {'API-KEY': API_KEY}

    response = requests.get(f"{baseURL}/cart/", headers=headers, params=params)
    if response.status_code == 200 and response.json():
        cart_id = response.json()['id']
        print(f'Cart id: {cart_id}')
    else:
        print(f"Failed to fetch cart: {response.status_code}")
        # Handle the case where the product is not found
        return render(request, 'webapp/error.html', {'message': 'Product not found'})
    print(f'Cart id: {cart_id}')

    if not cart_id:
        print(f"Failed to fetch cart: {response.status_code}")
        return redirect('webapp-cart')

    payload = {
        'cart': cart_id,
    }
    user_id = str(request.user.id)
    params = {'user_id': user_id}

    response = requests.post(f"{baseURL}/orders/create/", headers=headers, params=params, json=payload)

    if response.status_code == 200:
        return redirect('webapp-orders')
    else: 
        print(f"Erro with order: {response.content}")
        return redirect('webapp-cart')

def order_detail(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    headers = {'API-KEY': API_KEY}
    user_id = str(request.user.id)
    params = {'user_id': user_id}

    try:
        response = requests.get(f"{baseURL}/orders/{order_id}/", headers=headers, params=params)
        response.raise_for_status()

        order_data = response.json()
        items = order_data['items']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching order data: {e}")
        return  redirect('webapp')
    return render(request, 'webapp/order_detail.html', {'order': order_data, 'items': items})
    #return JsonResponse(order_data, safe=False)

def order_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    headers = {'API-KEY': API_KEY}
    user_id = str(request.user.id)
    params = {'user_id': user_id}
    try:
        response = requests.get(f"{baseURL}/orders/", headers=headers, params=params)
        response.raise_for_status()

        orders_data = response.json()
        orders = orders_data['results']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching orders data: {e}")
        return redirect('webapp')
    return render(request, 'webapp/order_list.html', {'orders': orders})
    #return JsonResponse(orders, safe=False)

def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    headers = {'API-KEY': API_KEY}
    user_id = str(request.user.id)
    params = {'user_id': user_id}


    response = requests.patch(f"{baseURL}/orders/{order_id}/cancel/", headers=headers, params=params)


    if response.status_code == 200:
        print('Order cancelled successfully')
        return redirect('webapp-orders')
    else:
        print('Order cannot be cancelled')
        return  redirect('webapp-orders')

def search_view(request):
    query = request.GET.get('q')
    max_price = request.GET.get('price_max')
    min_price = request.GET.get('price_min')
    category = request.GET.get('category')
    
    filters = {
        'search': query,
        'category': category,
        'price_min': min_price,
        'price_max': max_price
    }
    
    # Remove empty filter parameters
    filters = {k: v for k, v in filters.items() if v}
    
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/", params=filters, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('results', [])
    else:
        products = []
    
    return render(request, 'webapp/active_search_results.html', {'products': products})

def search_results(request):
    query = request.GET.get('q')
    max_price = request.GET.get('max_price')
    min_price = request.GET.get('min_price')
    category = request.GET.get('category')
    
    filters = {
        'search': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price
    }
    
    # Remove empty filter parameters
    filters = {k: v for k, v in filters.items() if v}
    headers = {'API-KEY': API_KEY}
    response = requests.get(f"{baseURL}/products/", params=filters, headers=headers)

    if response.status_code == 200:
        data = response.json()
        products = data.get('results', [])
    else:
        products = []
    return render(request, 'webapp/search_results.html', {'products': products})
