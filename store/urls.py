from django.urls import path
from .views import store_home, product_detail, add_to_cart, view_cart, update_quantity, remove_from_cart, checkout_store

urlpatterns = [
    path('', store_home, name='store_home'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/update/<int:item_id>/', update_quantity, name='update_quantity'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout_store, name='checkout_store'),

]
