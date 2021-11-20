from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from .models import Order
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Order
import weasyprint
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import os.path





def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
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
            request.session['order_id'] = order_id
            return redirect(reverse('payment:process'))
            # order_created.delay(order.id)
            # return render(request,
            #             'orders/order/created.html',
            #             {'order': order})
        
    else:
        form = OrderCreateForm()
    return render(request,
                'orders/order/create.html',
                {'cart':cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets = [weasyprint.CSS(os.path.join(settings.STATIC_ROOT, 'css', 'pdf.css'))])
    return response