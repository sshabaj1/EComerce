from io import BytesIO
import braintree
from braintree import client_token
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import weasyprint


# gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


# def payment_process(request):
#     order_id = request.session.get('order_id')
#     order = get_object_or_404(Order, id=order_id)
#     total_cost = order.get_total_cost()

#     if request.method == 'POST':
#         nonce = request.POST.get('payment_method_nonce', None)
#         result = gateway.transaction.sale({
#             'amount': f'{total_cost: .2f}',
#             'payment_method_nonce': nonce,
#             'options': {
#                 'submit_for_settlement': True
#             }
#         })
#         if result.is_success:
#             order.paid = True
#             order.braintree_id = result.transaction.id
#             order.save()
#             return redirect('payment:done')
#         else:
#             return redirect('payment:cancelled')
#     else:
#         client_token = gateway.client_token.generate()
#         return render(request,
#                     'payment/process.html',
#                     {'order': order,
#                     'client_token': client_token})



# def payment_done(request):
#     return render(request, 'payment/done.html')


# def payment_cancelled(request):
#     return render(request, 'payment/cancelled.html')



# instantiate Braintree payment gateway
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    total_cost = order.get_total_cost()
    if request.method == 'POST':
 # retrieve nonce
        nonce = request.POST.get('payment_method_nonce', None)
 # create and submit transaction
        result = gateway.transaction.sale({
            'amount': f'{total_cost:.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
 # mark the order as paid
            order.paid = True
 # store the unique transaction id
            order.braintree_id = result.transaction.id
            order.save()
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
 # generate token
        client_token = gateway.client_token.generate()
        return render(request,
                    'payment/process.html',
                    {'order': order,
                    'client_token': client_token})

def payment_done(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    subject, from_email, to = f'Genie - EE Invoice no. {order.id}', 'senadshabaj73@gmail.com', order.email
    text_content =  f'Please, find attachment the invoice for your recent purchase'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    msg.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    msg.send()
    return render(request, 'payment/done.html')


    
def payment_canceled(request):
    return render(request, 'payment/canceled.html')