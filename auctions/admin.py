from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Listing, Category, Bid, Comment

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Comment)
