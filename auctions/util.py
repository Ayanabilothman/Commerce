from .models import User, Category, Listing, Bid, Comment, ListingForm, BidForm, CommentForm

def close(item):
    max_bid = item.max_bid #beacuse start_bid is already updated when user bids in the item
    # all bids on the item
    item_bids = Bid.objects.filter(item=item)

    item.winner = item_bids.get(value=max_bid).bidder
    item.max_bid = max_bid
    item.availability = False
    item.save()

# add item to watchlist
def add_item(item, user):
    # .add beacuse it's manytomany field is couldn'y be direct assignment item.watcher = request.user X
    user.watchlist.add(item)

# remove item from watchlist
def remove_item(item, user):
    user.watchlist.remove(item)
