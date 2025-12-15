import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Listing
from .forms import ListingForm

# --- M-Pesa Helper Functions ---
def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
        r.raise_for_status()
        json_response = r.json()
        return json_response['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

# --- Standard Views ---
def home(request):
    featured = Listing.objects.filter(available=True).order_by('-created_at')[:3]
    return render(request, 'listings/home.html', {'featured': featured})

def search_listings(request):
    queryset = Listing.objects.all()
    
    campus = request.GET.get('campus')
    max_price = request.GET.get('max_price')
    bedrooms = request.GET.get('bedrooms')
    property_type = request.GET.get('property_type')
    
    if campus and campus != "All Campuses":
        queryset = queryset.filter(campus=campus)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if bedrooms:
        queryset = queryset.filter(bedrooms__gte=bedrooms)
    if property_type:
        queryset = queryset.filter(property_type=property_type)
        
    context = {
        'listings': queryset,
        'values': request.GET
    }
    return render(request, 'listings/search.html', context)

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    return render(request, 'listings/detail.html', {'listing': listing})

@login_required
def create_listing(request):
    if not request.user.is_landlord:
        return redirect('home')
        
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.landlord = request.user
            listing.save()
            return redirect('dashboard')
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})

@login_required
def landlord_dashboard(request):
    if not request.user.is_landlord:
        return redirect('home')
    user_listings = Listing.objects.filter(landlord=request.user)
    return render(request, 'listings/dashboard.html', {'listings': user_listings})

# --- M-Pesa Payment View ---
@login_required
def initiate_mpesa_payment(request, listing_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=400)

    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Ensure User has a phone number
    if not hasattr(request.user, 'phone_number') or not request.user.phone_number:
         return JsonResponse({'error': 'Please update your profile with a phone number first.'}, status=400)

    phone_number = str(request.user.phone_number).strip()
    
    # Format number for Sandbox (254...)
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+254'):
        phone_number = phone_number[1:]
    
    amount = int(listing.price)
    access_token = get_mpesa_access_token()
    
    if not access_token:
        return JsonResponse({'error': 'Could not authenticate with M-Pesa.'}, status=503)

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
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
        "TransactionDesc": f"Rent for {listing.title}"
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
        return JsonResponse({'error': str(e)}, status=500)