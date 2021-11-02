from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created


def order_create(request):
    print('hynn')
    cart = Cart(request)
    print('CART::', cart)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            print('order after save::',order)
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])

            #clear the cart
            print('order bf clear cart::',order)
            cart.clear()
            order_created.delay(order.id)
            print('order::',order)
            return render(request,
                        'orders/order/created.html',
                        {'order': order})
        
    else:
        form = OrderCreateForm()
    return render(request,
                'orders/order/create.html',
                {'cart':cart, 'form': form})