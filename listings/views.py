import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Listing
from .forms import ListingForm

stripe.api_key = settings.STRIPE_SECRET_KEY

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
    return render(request, 'listings/detail.html', {
        'listing': listing, 
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

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

@login_required
def create_checkout_session(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kes',  # <--- UPDATED TO KES
                    'unit_amount': int(listing.price * 100), 
                    'product_data': {
                        'name': f"Rent for {listing.title}",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri(f'/listing/{listing_id}/'),
        )
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})