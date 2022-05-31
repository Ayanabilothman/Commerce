from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import datetime
from . import util

from .models import User, Category, Listing, Bid, Comment, ListingForm, BidForm, CommentForm

def index(request):
    return render(request, "auctions/index.html", {
    'available_listings': Listing.objects.filter(availability=True)})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def item(request, id):
    # get the item object through its id
    item = Listing.objects.get(pk=id)
    context = {
    "listing": item, #item only beacuse I edit the __str__ function to return its name
    "bid_count": Bid.objects.filter(item=item).count(),
    "bidform": BidForm(use_required_attribute=False), # Formname(use_required_attribute=False) to disable the field to be required
    "commentform": CommentForm(use_required_attribute=False),
    "user": request.user,
    "watchers": item.watchlist_listing.all(),
    "winner": item.winner,
    "max_bid": item.max_bid,
    "comments": Comment.objects.filter(listing=item)}

    # if any user place a bid
    if request.POST.get("bid_submit"):
        # capture the submitted value
        submitted_data = BidForm(request.POST)
        if submitted_data.is_valid():
            # submitted_data['value'] is boundfield generated after posting data (the betwwen brackets is the name of the field)
            # it retuen the input tag coressponding to the django form field as an object
            # ex: <input type="number" name="value" required />
            # .data to access the data submitted itself
            # .data return a string even if the field is integer !

            # if the bid smaller than the current bid
            if int(submitted_data['value'].data) <= item.max_bid:
                message = "Your Bid must be higher than the current one!"
                context["message"] = message


            # if the bid more than the current bid
            else:
                # change the current bid to the new one
                item.max_bid = int(submitted_data['value'].data)
                item.save()
                # add the values of other model fields which don't found in the ModelForm
                data = submitted_data.save(commit=False)
                data.bidder = request.user
                data.item = item
                data.save()
                context["bid_count"] = Bid.objects.filter(item=item).count()
                '''return render(request, "auctions/test.html", {
                "bids": Bid.objects.all(),
                "item": item,
                "current_user": request.user
                })'''

    # if the user need to add a comment
    elif request.POST.get("comment_submit"):
        # Capture the submited comment
        submitted_data = CommentForm(request.POST)
        if submitted_data.is_valid():
            # add the values of other model fields which don't found in the ModelForm
            data = submitted_data.save(commit=False)
            data.comment_time = datetime.datetime.now()
            data.commenter = request.user
            data.listing = item
            data.save()
            #return HttpResponseRedirect(reverse("item", kwargs={"id": item.id}))

    # if the user need to add a listing to a watchlist
    elif request.POST.get("add_to_list"):
        util.add_item(item, request.user)

    # if the user need to remove a listing from the watchlist
    elif request.POST.get("remove_from_list"):
        util.remove_item(item, request.user)

    elif request.POST.get("close_submit"):
        util.close(item)
        context["winner"] = item.winner
        context["close_time"] = datetime.datetime.now()
        
    return render(request, "auctions/item.html", context) #item.watchlist_listing.all() # get all the users who add this item into their watchlist

@login_required
def create(request):
    if request.method == "POST":
        submitted_data = ListingForm(request.POST)
        if submitted_data.is_valid():
            # That's useful when you get most of your model data from a form,
            # but you need to populate some null=False fields with non-form data.
            #Saving with commit=False gets you a model object,
            #then you can add your extra data and save it.
            data = submitted_data.save(commit=False)
            data.owner = request.user
            data.creation_dt = datetime.datetime.now()
            data.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {
    "listing_form": ListingForm(),
    #"user_id": request.user.id
    })

def categories(request):
    return render(request, "auctions/categories.html", {
    "categories": Category.objects.all()
    })

def category(request, name):
    category = Category.objects.get(name=name)
    return render(request, "auctions/category-item.html", {
    "listings": Listing.objects.filter(category_id=category.id),
    "category": name
    })


def watchlist(request):
    return render(request, "auctions/watchlist.html", {
    "fav_listings": request.user.watchlist.all()})
