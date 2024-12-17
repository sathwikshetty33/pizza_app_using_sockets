from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import *
# Create your views here.
def home(request):
    pizzas = pizza.objects.all()
    orders = order.objects.filter(user=request.user.id)
    context = {'pizza' : pizzas, 'order' : orders}
    return render(request,'pizza/index.html',context)

def orderview(request, order_id ):
    orders = order.objects.filter(order_id=order_id).first()
    if order is None:
        return redirect('/')
    context = {'orders' : orders}
    return render(request,'pizza/order.html',context)


@csrf_exempt
def order_create(request):
    if request.method == 'POST':
        pizza_id = request.POST.get('pizza_id')
        pizzas = get_object_or_404(pizza, id=pizza_id)
        orders = order.objects.create(pizza=pizzas, amount=pizzas.price,user = request.user)

        # Generate the URL for the order details page
        order_url = f"order/{orders.order_id}"

        # Return JSON response with the required details
        return JsonResponse({
            'id': orders.id,
            'pizza_name': pizzas.name,
            'price': pizzas.price,
            'order_url': order_url,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)