from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import transaction



# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)
    rgpd_consent = models.BooleanField(default=False)
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

class Menu(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large')
    ]
    FRIES_CHOICES = [
        ('NF', 'Normal Fries'),
        ('P', 'Potatoes'),
        ('CF', 'Cheesy Fries')
    ]

    picture = models.URLField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=230)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    ingredients = models.CharField(max_length=130)
    quantity = models.PositiveIntegerField()
    type = models.CharField(max_length=100)
    size = models.CharField(max_length=1, choices=SIZE_CHOICES, blank=True, null=True)
    fries_type = models.CharField(max_length=2, choices=FRIES_CHOICES, blank=True, null=True)
    sauce_type = models.CharField(max_length=100, blank=True, null=True)
    supplement_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed')
    ]

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_points = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    promo_code = models.CharField(max_length=50, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points_updated = models.BooleanField(default=False)

    def calculate_points(self):
        # 1 point for every 10 DH spent
        return int(self.total_price // 10)

    def save(self, *args, **kwargs):
        if self.status == 'C' and not self.points_updated:
            self.total_points = self.calculate_points()
            
            # Update the user's total points
            with transaction.atomic():
                self.user.total_points += self.total_points
                self.user.save()

                # Mark points as updated
                self.points_updated = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey('Menu', on_delete=models.CASCADE)
    fries_type = models.CharField(max_length=2, choices=Menu.FRIES_CHOICES)
    sauces = models.CharField(max_length=255, blank=True, null=True)
    supplements = models.CharField(max_length=255, blank=True, null=True)
    supplement_quantity = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    customization = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OrderItem {self.id} for Order {self.order.id}"

class PointsHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('E', 'Earned'),
        ('S', 'Spent')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_histories')
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PointsHistory {self.id} for User {self.user.id} on {self.transaction_date}"

class Comment(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.id} by User {self.user.id} on Order {self.order.id}"