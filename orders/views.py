from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from .models import Order







def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])

            #clear the cart
            cart.clear()
            order_id = order.id
            order = Order.objects.get(id=order_id)
            subject, from_email, to = f'Order nr. {order_id}', 'senadshabaj73@gmail.com', order.email
            text_content =  f'Dear {order.first_name}, \n \n' \
                    f'You have successfully placed an order.' \
                    f'Your order ID is {order_id}.'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.send()
            # order_created.delay(order.id)
            return render(request,
                        'orders/order/created.html',
                        {'order': order})
        
    else:
        form = OrderCreateForm()
    return render(request,
                'orders/order/create.html',
                {'cart':cart, 'form': form})