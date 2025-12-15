from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from listings import views as listing_views
from users import views as user_views  # <--- IMPORT THIS

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Listings
    path('', listing_views.home, name='home'),
    path('search/', listing_views.search_listings, name='search'),
    path('listing/<int:pk>/', listing_views.listing_detail, name='detail'),
    path('dashboard/', listing_views.landlord_dashboard, name='dashboard'),
    path('create-listing/', listing_views.create_listing, name='create_listing'),
    
    # Auth System (Login/Register/Logout)
    path('register/', user_views.register, name='register'), # <--- ADD THIS LINE
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from django.urls import path
from . import views

urlpatterns = [
    # ... existing paths ...
    path('pay/mpesa/<int:listing_id>/', views.initiate_mpesa_payment, name='mpesa_payment'),
]