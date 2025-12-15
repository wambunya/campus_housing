import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Helper to get Access Token
def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    json_response = r.json()
    return json_response['access_token']

@login_required
def initiate_mpesa_payment(request, listing_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    listing = get_object_or_404(Listing, pk=listing_id)
    phone_number = request.user.phone_number # Ensure user model has this field
    
    # Format phone number (Must be 2547XXXXXXXX)
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    
    amount = int(listing.price)
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    # Generate Password
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    passkey = settings.MPESA_PASSKEY
    shortcode = settings.MPESA_BUSINESS_SHORTCODE
    password_str = shortcode + passkey + timestamp
    password = base64.b64encode(password_str.encode()).decode('utf-8')

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"Rent-{listing.id}",
        "TransactionDesc": f"Rent payment for {listing.title}"
    }

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})