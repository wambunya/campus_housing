from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Listing
from .forms import ListingForm

def home(request):
    # Featured listings (e.g., newest 3)
    featured = Listing.objects.filter(available=True).order_by('-created_at')[:3]
    return render(request, 'listings/home.html', {'featured': featured})

def search_listings(request):
    queryset = Listing.objects.all()
    
    # Filtering Logic (Replaces React filteredListings)
    campus = request.GET.get('campus')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    bedrooms = request.GET.get('bedrooms')
    
    if campus and campus != "All Campuses":
        queryset = queryset.filter(campus=campus)
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
    if bedrooms:
        queryset = queryset.filter(bedrooms__gte=bedrooms)
        
    context = {
        'listings': queryset,
        'values': request.GET # Preserve search values in form
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
            # In a real app, use Geocoding API here to set lat/long based on address
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