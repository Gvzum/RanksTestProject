from django.urls import path

from .views import *

app_name = 'runki'

urlpatterns = [
    path('item/', view_list_items, name='ListOfItems'),
    path('item/<int:pk>/', view_item, name='ItemDetail'),
    path('buy/<int:pk>/', view_buy_item, name='BuyItem'),
    path('add_to_cart/', view_add_cart, name='Cart'),
    path('checkout_cart/', view_checkout_cart, name='CheckoutCart'),
]
