from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.template.defaultfilters import slugify
import secrets
from django.db.models.signals import post_save
# Create your models here.

class UserProfile(models.Model): 
    UserAccount = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    
    UserID = models.AutoField(primary_key=True)
    Slug = models.SlugField(unique=True, null=True)
    Favourites = models.ManyToManyField('Magazine', related_name='Favourite%(class)s', blank= True)
    Membership = models.DateField(null=True)
    MembershipID = models.IntegerField(null=True)
    
    def __str__(self):
        return self.UserAccount.username

    def save(self, *args, **kwargs):
        self.Slug = slugify(self.UserAccount.username)
        super(UserProfile, self).save(*args, **kwargs)
        
    """
    Stuff to be added:
    Encoded payment information
    """

class Magazine(models.Model):
    MagazineID = models.AutoField(primary_key=True)
    Slug = models.SlugField(unique=True, null=True)
    Name = models.CharField(max_length=50)
    Description = models.CharField(max_length=800)
    Image = models.ImageField(upload_to='magazine_images', blank=True)
    Date = models.DateField()
    URL = models.URLField(blank=True)
    Categories = models.ManyToManyField('Category', blank=True)
    Discount = models.CharField(unique=True, null=True, max_length=10)
    Price = models.DecimalField(max_digits=5, decimal_places=2)
    DiscountPrice = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return self.Name

    def save(self, *args, **kwargs):
        self.Slug = slugify(self.Name)
        super(Magazine, self).save(*args, **kwargs) 
    
    
    """
    Stuff to be added:
    Issues class? (Many to one) - price, discountprice, discount code, image, url?
    
    """

class Category(models.Model):
    
    CategoryID = models.AutoField(primary_key=True)
    Slug = models.SlugField(unique=True, null = True)
    Name = models.CharField(max_length=30)
    Mags = models.ManyToManyField('Magazine', blank = True)
    
    def __str__(self):
        return self.Name

    def save(self, *args, **kwargs):
        self.Slug = slugify(self.Name)
        super(Category, self).save(*args, **kwargs)
    
    
    """To be added:
    Slug field for URLs
    """
    

    
    
