from django.urls import path
from .views import (
    cart_view, add_to_cart, product_detail, product_list, decrease_cart_item, 
    delete_cart_item, login, register, logout, increase_cart_item, submit_review, 
    create_order, order_detail, order_list, cancel_order, search_view, search_results, review_list
)
from django.conf import settings
from django.conf.urls import static

urlpatterns = [
    path('', product_list, name='webapp'),
    path('<slug:slug>/review/create/', submit_review, name='submit-review'),
    path('<slug:slug>/reviews/', review_list, name='webapp-reviews'),
    path('cart/', cart_view, name='webapp-cart'),
    path('cart/add/<slug:slug>/', add_to_cart, name='webapp-add-to-cart'),
    path('search/', search_view, name='webapp-search'),
    path('results/', search_results, name='webapp-search-results'),
    path('order/create/', create_order, name='webapp-order' ),
    path('orders/', order_list, name='webapp-orders'),
    path('order/<int:order_id>/', order_detail, name='webapp-order-detail'),
    path('order/<int:order_id>/cancel/', cancel_order, name='webapp-cancel-order'),
    path('cart/increase/<int:product_id>/', increase_cart_item, name='webapp-cart-increase'),
    path('cart/decrease/<int:product_id>/', decrease_cart_item, name='webapp-cart-decrease'),
    path('cart/delete/<int:product_id>/', delete_cart_item, name='webapp-cart-item-delete'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('<slug:slug>/', product_detail, name='webapp-product-details'),

]