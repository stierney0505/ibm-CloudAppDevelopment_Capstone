from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from . import restapis
from . import models

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
# def contact(request):
def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['user']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/djangoapp/')

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    context = {}
    logout(request)
    return redirect('/djangoapp/')
# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    
    elif request.method == 'POST':
        username = request.POST['user'];
        password = request.POST['password'];
        fname = request.POST['first_name'];
        lname = request.POST['last_name'];
        account = False

        try:
            User.objects.get(username=username)
            account = True
        except:
            print("error")

        if not account:
            user = User.objects.create_user(username=username, first_name = fname, last_name = lname, password=password)

            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html')
# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = 'https://stierney0505-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get'
        # Get dealers from the URL
        context = {"dealerships": restapis.get_dealers_from_cf(url)}
        # Concat all dealer's short name
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://stierney0505-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id=" + str(dealer_id);
        context = {"dealerships": restapis.get_dealer_reviews_from_cf(url, dealer_id)}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    if request.method == "GET":
        dealersid = dealer_id
        url = "https://stierney0505-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/dealer-get?dealerId={0}".format(dealersid)
        context = {
            "cars": models.CarModel.object.all(),
            "dealers": restapis.get_dealers_fromcf(url),
        }
        return render(request, 'django/add_review.html', context)
    elif request.method == "POST":
        if request.user.is_authenticated:
            form = request.POST 
            review = {
                "name": "{request.user.first_name} {request.user.last_name}",
                "dealership": dealer_id,
                "review": form["content"],
                "purchase": form.get("purchasecheck"),
                }
            if form.get("purchasecheck"):
                review["purchase_date"] = datetime.strptime(form.get("purchasedate"), "%m/%d/%Y").isoformat()
                car = models.CarModel.objects.get(pk=form["car"])
                review["car_make"] = car.carmake.name
                review["car_model"] = car.name
                review["car_year"]= car.year.strftime("%Y")
            json_payload = {"review": review}
            print (json_payload)
            url = "https://stierney0505-5000.theiadocker-3-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/reviews/review-post"
            restapis.post_request(url, json_payload, dealerId=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return redirect("/djangoapp/login")