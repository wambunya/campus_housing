from django.db import models
from django.conf import settings

class Listing(models.Model):
    CAMPUS_CHOICES = [
        ('Tech University', 'Tech University'),
        ('State University', 'State University'),
    ]
    
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('shared', 'Shared Room'),
    ]

    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=300)
    campus = models.CharField(max_length=100, choices=CAMPUS_CHOICES)
    distance_from_campus = models.FloatField(help_text="Distance in miles")
    
    # Specs
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    sqft = models.IntegerField(null=True, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    
    # Media
    image = models.ImageField(upload_to='listing_photos/')
    
    # Amenities (Stored as boolean flags for simple filtering)
    has_wifi = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    
    # Status
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=True, null=True) # For Maps
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title