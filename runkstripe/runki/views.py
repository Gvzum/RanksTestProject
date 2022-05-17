import json
import stripe

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import (Item,
                     Order,
                     OrderItem)

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = '2020-08-27; orders_beta=v3'


@login_required(login_url='/admin/')
def view_list_items(request):
    context = dict()
    context['title'] = 'Items'
    context['items'] = Item.objects.all()
    context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    context['cart_size'] = order.get_total_items

    return render(request, 'runki/list_item.html', context)


@login_required(login_url='/admin/')
def view_item(request, pk):
    context = dict()

    try:
        item = Item.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponse('Doesnt have any item by this id')

    context['title'] = item.name
    context['item'] = item
    context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY

    return render(request, 'runki/item.html', context)


@login_required(login_url='/admin/')
def view_buy_item(request, pk):
    item = Item.objects.get(pk=pk)
    order = Order.objects.create(user=request.user, complete=True)
    OrderItem.objects.create(order=order, item=item, quantity=1)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.name,
                },
                'unit_amount': item.price
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/item',
        cancel_url='http://127.0.0.1:8000/item',
    )

    return JsonResponse(session, safe=False)


@login_required(login_url='/admin/')
def view_add_cart(request):
    data = json.loads(request.body)
    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    item, _ = Item.objects.get_or_create(pk=data['item_pk'])
    OrderItem.objects.get_or_create(order=order,
                                    item=item,
                                    quantity=1)

    return JsonResponse('Added to cart', safe=False)


@login_required(login_url='/admin/')
def view_checkout_cart(request):
    order, _ = Order.objects.get_or_create(user=request.user, complete=False)
    order.complete = True
    order.save()
    line_items = list()

    for i in order.orderitem_set.all():
        item_data = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': i.item,
                },
                'unit_amount': i.item.price,
            },
            'quantity': i.quantity,
        }

        line_items.append(item_data)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/item',
        cancel_url='http://127.0.0.1:8000/item',
    )

    return JsonResponse(session, safe=False)

