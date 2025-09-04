from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db import models as dj_models
from django.core.exceptions import ValidationError


# Create your models here.

class MenuCategory(models.Model):
    menu_category_name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.menu_category_name

class DrinksCategory(models.Model):
    drink_category_name = models.CharField(max_length=200)

    def __str__(self):
        return self.drink_category_name
    
class MenuFood(models.Model):
    food_name= models.CharField(max_length=100)
    description=models.TextField()
    price=models.DecimalField(max_digits=5, decimal_places=2)
    category_id = models.ForeignKey(MenuCategory, on_delete=models.PROTECT, default=None, related_name="category_name")
    image= models.ImageField(upload_to='menu_images/',null=True, blank=True)

    def __str__(self):
        return self.food_name

class Drinks(models.Model):
    drink_name = models.CharField(max_length=200)
    price = models.IntegerField()
    categories = models.ManyToManyField(DrinksCategory, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='drinks_images/', null=True, blank=True)

    def __str__(self):
        return self.drink_name
    
class ContactMessage(models.Model):
    name= models.CharField(max_length=100)
    subject=models.CharField(max_length=200)
    email=models.EmailField()
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    party_size= models.IntegerField()
    table = models.ForeignKey('Table', on_delete=models.SET_NULL, null=True, blank=True)
    is_shared = models.BooleanField(default=False)

    #prevent negative party size in database 
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(party_size__gt=0),
                name='party_size_gt_0'
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.date} at {self.time}"
    
    def clean(self):
    # Only check if user is set
        if self.user:
            existing = Reservation.objects.filter(user=self.user, date=self.date)
            # Exclude self in case of updating an existing reservation
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("You can only reserve one table per day.")

class Table(models.Model):
    capacity = models.IntegerField()
    table_number = models.CharField(max_length=50, unique=True)
    allows_shared = models.BooleanField(default=False, help_text="True means shared, False is private only.")

    def __str__(self):
        return f"Table {self.table_number} (Seats {self.capacity}, {'Shared' if self.allows_shared else 'Private'})"

    def has_future_reservations(self):
        current = now()
        today = current.date()
        now_time = current.time()
        return Reservation.objects.filter(
            table=self
        ).filter(
            dj_models.Q(date__gt=today) |
            dj_models.Q(date=today, time__gt=now_time)
        ).exists()


class Review(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=60)  # used if the user is not logged in
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  #  get approved by staff before showing

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        who = self.user.username if self.user else self.name
        return f"{who} ({self.rating}★)"
    











