from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from django.forms import ModelForm, widgets

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', related_name="watchlist_listing", blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Listing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.URLField(blank=True, null=True)
    creation_dt = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_listing") #user may own more than one listing but listing owned only by one user
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True) #user may win more than one listing but listing won only by one user
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    availability = models.BooleanField(default=True)
    start_bid = models.IntegerField(default=0)
    max_bid =  models.IntegerField()


    def save(self,*args,**kwargs):
        # to make the initial value of max_bid to be equal to start_bid by default
        if not self.max_bid:
            self.max_bid = self.start_bid

        if not self.image:
            self.image = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"

        if not self.category:
            self.category = Category.objects.get(name="No Category")

        super().save(*args,**kwargs)

    def __str__(self):
        return self.name

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['name', 'description', 'image', 'category', 'start_bid']

class Bid(models.Model):
    value = models.IntegerField(blank=True,null=True, verbose_name="") #verbose_name="" equavilent to label="" in forms but verbose for models
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)#will be dropdown menu having all objects in Listing Table (in Admimn interface)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)#will be dropdown menu having all objects in User Table (in Admimn interface)

    def __str__(self):
        return f"{self.bidder.username} bids on {self.item.name}"

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['value']

class Comment(models.Model):
    comment_time = models.DateTimeField(null=True)
    content = models.TextField(verbose_name="")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commenter} commented on {self.listing}"

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        widgets = {
            'content': forms.Textarea(attrs={'class': 'commentarea', 'placeholder': 'Leave a Comment!'}),
        }
        fields = ['content']
