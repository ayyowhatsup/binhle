from django.shortcuts import render, redirect
from cart.cart import get_cart_items, cart_subtotal  as get_cart_subtotal
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import requests
import json
import urllib
from .vnpay import vnpay
from datetime import datetime
from .models import Order, OrderItem
from cart.cart import CART_ID_SESSION_KEY
import sendgrid
from django.forms.models import model_to_dict
# Create your views here.
def checkout(request, template_name = 'payment/checkout.html'):
    
    cart_items = get_cart_items(request)
    if not cart_items:
        return redirect('cart')
    cart_subtotal = get_cart_subtotal(request)
    if request.method == 'POST':
        """
        Preview order valid by GHN
        """
        rc = request.POST
        headers = {'Token': settings.GHN_TOKEN,'ShopId': settings.GHN_SHOP_ID, 'Content-Type': 'application/json'}
        body = {}
        body['to_name'] = rc.get('name', '')
        body['to_phone'] = rc.get('phone_number','')
        body['to_address'] = rc.get('shipping_address', '')
        body['to_ward_code'] = rc.get('shipping_ward', '').split('-')[0]
        body['to_district_id'] = int(rc.get('shipping_district','').split("-")[0])
        body['height'] = 5
        body['length'] = 30
        body['width'] = 30
        body['payment_type_id'] = 1
        body['required_note'] = 'KHONGCHOXEMHANG'
        body['service_id'] = int(rc.get('shipping_service', ''))
        body['items'] = []
        weight = 0
        for cart_item in cart_items:
            weight += cart_item.quantity * cart_item.product.weight
            t = {}
            t['name'] = cart_item.product.name
            t['quantity'] = cart_item.quantity
            body['items'].append(t)
        body['weight'] = weight
        preview_url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/preview'
        response = requests.post(preview_url, headers=headers, json=body)
        if response.json()['code'] != 200:
            error = response.json()['code_message_value']
        else:
            """
            Create order
            """
            ## Order_id = cart_id ... 
            order_id = request.session[CART_ID_SESSION_KEY]
            shipping_fee = response.json()['data']['total_fee']
            product_price = cart_subtotal
            amount = shipping_fee + product_price
            new_order = Order.objects.create(id = order_id, name = rc.get('name', ''), email = rc.get('email', ''), phone_number = rc.get('phone_number',''), 
            shipping_province = rc.get('shipping_province','').split("-")[1], shipping_district = rc.get('shipping_district','').split("-")[1],
            shipping_ward = rc.get('shipping_ward', '').split('-')[1], shipping_address = rc.get('shipping_address', ''), additional_note = rc.get('additional_note', ''),
            shipping_fee = shipping_fee, product_price = product_price, total = amount)

            if request.user.is_authenticated:
                new_order.user = request.user
                new_order.save()

            for cart_item in cart_items:
                product = cart_item.product
                quantity = cart_item.quantity
                price = cart_item.product.price
                order_item = OrderItem.objects.create(product = product, quantity = quantity, price = price, order = new_order)
            """
            Generate VNPay url and redirect
            """
            order_type = 150000 # stationery product
            order_id = new_order.id
            order_desc = f"Thanh toan cho don hang {order_id}"
            bank_code = ''
            language = ''
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = int(amount) * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type
            # Check language, default: vn
            if language and language != '':
                vnp.requestData['vnp_Locale'] = language
            else:
                vnp.requestData['vnp_Locale'] = 'vn'
                # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if bank_code and bank_code != "":
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
    provinces = get_province(request)['data']
    return render(request, template_name, locals())

def get_province(request):
    headers = {'Token': settings.GHN_TOKEN, 'Content-Type': 'application/json'}
    response = requests.get('https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/province', headers=headers)
    return response.json()

def get_district(request):
    province_id  = request.POST['province_id']
    headers = {'Token': settings.GHN_TOKEN, 'Content-Type': 'application/json'}
    response = requests.get(f'https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/district?province_id={province_id}', headers=headers)
    return HttpResponse(json.dumps(response.json()['data']), content_type = 'application/json')

def get_town(request):
    district_id = request.POST['district_id']
    headers = {'Token': settings.GHN_TOKEN, 'Content-Type': 'application/json'}
    response = requests.get(
            f'https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id={district_id}', headers=headers)
    return HttpResponse(json.dumps(response.json()['data']), content_type = 'application/json')

def get_services(request):
    district_id = request.POST['district_id']
    headers = {'Token': settings.GHN_TOKEN,'ShopId': settings.GHN_SHOP_ID, 'Content-Type': 'application/json'}
    get_services_url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/available-services'
    body1 = {}
    body1['shop_id'] = int(settings.GHN_SHOP_ID)
    body1['from_district'] = 1542
    body1['to_district'] = int(district_id)
    response = requests.post(get_services_url, headers=headers, json=body1)
    return HttpResponse(json.dumps(response.json()['data']), content_type = 'application/json')

def get_shipping_fee(request):
    body = request.POST
    headers = {'Token': settings.GHN_TOKEN,
               'ShopId': settings.GHN_SHOP_ID, 'Content-Type': 'application/json'}
    body2 = {}
    body2['height'] = 5
    body2['length'] = 30
    body2['width'] = 30
    weight = 0
    cart_items = get_cart_items(request)
    for cart_item in cart_items:
        weight += cart_item.quantity * cart_item.product.weight
    body2['insurance_value'] = int(get_cart_subtotal(request))
    body2['weight'] = weight
    body2['service_id'] = int(body['service_id'])
    body2['to_district_id'] = int(body['shipping_district'])
    body2['from_district_id'] = 1542  # Quận Hà Đông
    body2['to_ward_code'] = str(body['shipping_ward'])
    body2['coupon'] = None
    response = requests.post(
        'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee', headers=headers, json=body2)
    if(response.json()['code'] == 200):
        return HttpResponse(json.dumps(response.json()['data']), content_type = 'application/json')
    else:
        return HttpResponse(json.dumps({'code': response.json()['code'], 'message': response.json()['code_message_value']}), content_type = 'application/json', status = response.json()['code'])
    
def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({"Message": "Order Not Found", "RspCode": "01"})
            firstTimeUpdate = order.status == Order.SUBMITTED
            total_amount = int(amount) / 100
            if total_amount == int(order.total):
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        order.status = Order.PROCESSED
                        order.transaction_id = vnp_TransactionNo
                        order.save(update_fields=['status', 'transaction_id'])

                        """
                        CREATE A GIAOHANGNHANH ORDER
                        """
                        url_create_order = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create'
                        headers = {'Token': settings.GHN_TOKEN,
                                   'Content-Type': 'application/json', 'ShopId': settings.GHN_SHOP_ID}
                        """
                        :( TODO://
                        """
                        url_get_district = 'https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/district'
                        district_resp = requests.get(url_get_district, headers=headers)
                        my_dict = {d['DistrictName']: d['DistrictID'] for d in district_resp.json()['data']}
                        district_id = my_dict.get(order.shipping_district)
                        get_services_url = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/available-services'
                        body1 = {}
                        body1['shop_id'] = int(settings.GHN_SHOP_ID)
                        body1['from_district'] = 1542  # Quận Hà Đông
                        body1['to_district'] = district_id
                        response = requests.post(get_services_url, headers=headers, json=body1)
                        service_id = response.json()['data'][0]['service_id']

                        weight = 0
                        body = {}
                        body['to_name'] = order.name
                        body['to_phone'] = order.phone_number
                        body['to_address'] = order.shipping_address
                        body['to_province_name'] = order.shipping_province
                        body['to_district_name'] = order.shipping_district
                        body['to_ward_name'] = order.shipping_ward
                        body['height'] = 5
                        body['length'] = 30
                        body['width'] = 30
                        body['service_id'] = service_id
                        body['payment_type_id'] = 1
                        body['required_note'] = 'KHONGCHOXEMHANG'
                        body['items'] = []

                        for item in order.order_items.all():
                            t = dict()
                            t['name'] = item.product.name
                            t['quantity'] = item.quantity
                            t['weight'] = item.product.weight
                            body['items'].append(t)
                            weight += item.product.weight
                            
                        body['weight'] = weight
                        body['insurance_value'] = int(order.total)
                        body['client_order_code'] = order.id

                        res = requests.post(url=url_create_order, headers=headers, json=body)

                        """
                        SEND EMAIL RECEIPT TO CUSTOMER
                        """
                        sg = sendgrid.SendGridAPIClient(
                            api_key=settings.SENDGRID_EMAIL_HOST_PASSWORD)
                        dynamic_template_data = model_to_dict(order)
                        dynamic_template_data['shipping_fee'] = float(dynamic_template_data['shipping_fee'])
                        dynamic_template_data['product_price'] = float(dynamic_template_data['product_price'])
                        dynamic_template_data['total'] = float(dynamic_template_data['total'])
                        dynamic_template_data['order_items'] = []
                        for order_item in order.order_items.all():
                            item = {}
                            item['product'] = order_item.product.name
                            item['quantity'] = order_item.quantity
                            item['price'] = float(order_item.price)
                            item['total'] = float(order_item.quantity * order_item.price)
                            dynamic_template_data['order_items'].append(item)
                        data = {}
                        personalizations = [{}]
                        personalizations[0]["dynamic_template_data"] = dynamic_template_data
                        personalizations[0]["to"] = [{"email": order.email}]
                        data["from"] = {"email": settings.SENDGRID_SEND_FROM}
                        data["template_id"] = settings.SENDGRID_TEMPLATE_ID
                        data["personalizations"] = personalizations
                        res = sg.client.mail.send.post(request_body=data)
                    else:
                        order.delete()
                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result

def payment_return(request, template_name = 'payment/payment_return.html'):
    respone_code = {"00": "Giao dịch thành công", "07": "Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).,",
                    "09": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.",
                    "10": "Giao dịch không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần",
                    "11": "Giao dịch không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.",
                    "12": "Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.",
                    "13": "Giao dịch không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP). Xin quý khách vui lòng thực hiện lại giao dịch.",
                    "24": "Giao dịch không thành công do: Khách hàng hủy giao dịch",
                    "51": "Giao dịch không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.",
                    "65": "Giao dịch không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.",
                    "75": "Ngân hàng thanh toán đang bảo trì.",
                    "79": "Giao dịch không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định. Xin quý khách vui lòng thực hiện lại giao dịch",
                    "99": "Các lỗi khác"}
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        transaction_id = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                order = Order.objects.get(id = order_id)
                message = respone_code[vnp_ResponseCode]
            else:
                message = respone_code[vnp_ResponseCode]
        else:
            message = "Sai checksum"
        return render(request, template_name, locals())
    else:
        return redirect('home_page')

def order_tracking(request, template_name = 'payment/order_tracking.html'):
    if request.method == 'POST':
        order_id = request.POST.get('order_id','')
        email = request.POST.get('email','')
        if order_id and email:
            try:
                order = Order.objects.get(id = order_id, email = email)
                url_get_order_info = 'https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/detail-by-client-code'
                headers = {'Token': settings.GHN_TOKEN, 'Content-Type': 'application/json'}
                body = {}
                body['client_order_code'] = order.id
                res = requests.post(url_get_order_info, headers=headers, json=body)
                data = res.json()['data']
            except Order.DoesNotExist:
                error = "Không tìm thấy đơn hàng hợp lệ!"
    return render(request, template_name, locals())

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
