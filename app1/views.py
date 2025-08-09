from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import UserForm, JobForm, OfferForm, ReviewForm, CategoriesForm, PickCategoryForm, LoginForm    #, CompletedForm
from app1.models import User, JobPost, UserProfile, Messages, Offer, Job, Conversation, JobCategory
import json
import requests

def loginView(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is not None:
            login(request, user)
            userID = request.POST['username']
            userprofileID = get_object_or_404(User, username=userID)
            userprofileID = userprofileID.userprofile.id
            userprofile = get_object_or_404(UserProfile, pk=userprofileID)
            #if not(userprofile.isCustomer) and userprofile.jobCategory is None:
            if userprofile.jobCategory is None:
                return redirect('add_categories')
            else:
                return redirect('dashboard')
        else:
            return HttpResponseForbidden("Invalid credentials")

    return render(request, './login.html', {
        'form': LoginForm()
    })

def addCategoriesView(request):


    form = CategoriesForm()


    if request.method == "POST":
        form = CategoriesForm(request.POST)

        if form.is_valid():
            #print("here")
            API_KEY="<INSERT_API_KEY_HERE>" #TODO
            address = form.instance.location
            params = {
                'key':API_KEY,
                'address':address
            }
            base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
            response = requests.get(base_url, params=params).json()
            response.keys()

            if response['status'] == 'OK':
                #print(response)
                geometryObject = response['results'][0]['geometry']
                place_id = response['results'][0]['place_id']
                lat = geometryObject['location']['lat']
                lng = geometryObject['location']['lng']
                jobCatID = request.POST.get('jobCategory')
                userprofileID = request.user.userprofile.id
                userprofile = get_object_or_404(UserProfile, pk=userprofileID)
                userprofile.placeID = place_id
                userprofile.lat = float(lat)
                userprofile.lng = float(lng)
                userprofile.jobCategory = get_object_or_404(JobCategory, pk=jobCatID)
                userprofile.mileageRange = form.instance.mileageRange
                userprofile.location = form.instance.location
                if request.user.userprofile.isCustomer:
                    userprofile.preferRating = form.instance.preferRating
                userprofile.save()
                return redirect('dashboard')

    return render(request, './profile_settings.html', {"form":form})

def signupView(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.save()
            profile_type = request.POST.get('profile_type')
            if profile_type == "customer":
                userprofile = UserProfile.objects.create(user=user, isCustomer=True)
                user.userprofile.save()
                login(request, user)
                return redirect('add_categories')
            elif profile_type == "builder":
                userprofile = UserProfile.objects.create(user=user, isCustomer=False)
                user.userprofile.save()
                login(request, user)
                return redirect('add_categories')
    return render(request, './signup.html', {"form":form})

def homepageView(request, userID):
    posts = {}
    user = get_object_or_404(User, pk=userID)
    if user.userprofile.isCustomer:
        customerJobCat = get_object_or_404(JobCategory, pk=user.userprofile.jobCategory.id)
        customerRange = float(user.userprofile.mileageRange)
        recommendedPosts = {}
        if user.userprofile.preferRating == "Ratings":
            if user.userprofile.jobCategory.name == "All":
                recommendedBuilders = UserProfile.objects.filter(isCustomer = False).order_by('-avgRating')
            else:
                recommendedBuilders = UserProfile.objects.filter(isCustomer = False, jobCategory=customerJobCat).order_by('-avgRating')
        elif user.userprofile.preferRating == "Proximity":
            if user.userprofile.jobCategory.name == "All":
                recommendedBuilders = UserProfile.objects.filter(isCustomer = False)
            else:
                recommendedBuilders = UserProfile.objects.filter(isCustomer = False, jobCategory=customerJobCat)
            for builder in recommendedBuilders:
                builderLoc = builder.placeID
                customerLoc = user.userprofile.placeID
                #print(builderLoc,customerLoc)
                #url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:"+builderLoc+"&destinations=place_id:"+customerLoc+"&key=<INSERT_API_KEY_HERE>" #TODO
                #payload={}
                #headers = {}
                #response = requests.request("GET", url, headers={}, data={})
                #response = response.json()
                #distance = str(response['rows'][0]['elements'][0]['distance']['text'])

                #distanceSplit = distance.split(" ")
                #print(distanceSplit)
                ##distance = 0.62137 * float(distanceSplit[0]) # converts km to miles

                distance = 0.621

                distance = round(distance,2)
                #travelTime = str(response['rows'][0]['elements'][0]['duration']['text'])
                #if builder.actualMileageVal <= customerRange:
                builder.actualMileageVal = distance
                builder.save()
            recommendedBuilders = recommendedBuilders.filter(actualMileageVal__lte=customerRange).order_by('actualMileageVal') # less than customer's max mileage range
            #recommendedBuilders = UserProfile.objects.filter(isCustomer = False, jobCategory=customerJobCat).order_by('actualMileageVal')
    else:
        posts = JobPost.objects.filter(accepted=False,finished=False).order_by('-id')
        recommendedBuilders = {}
        recommendedPosts = {}
        builderJobCat = get_object_or_404(JobCategory, pk=user.userprofile.jobCategory.id)
        builderRange = float(user.userprofile.mileageRange)
        builderLoc = user.userprofile.placeID

        if user.userprofile.jobCategory.name == "All":
            recommendedPosts = JobPost.objects.all().filter(accepted=False,finished=False)
        else:
            recommendedPosts = JobPost.objects.all().filter(accepted=False,finished=False,jobCategory=builderJobCat)

        for post in recommendedPosts:
            customerLoc = post.placeID
            url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=place_id:"+builderLoc+"&destinations=place_id:"+customerLoc+"&key=<INSERT_API_KEY_HERE>"
            response = requests.request("GET", url, headers={}, data={})
            response = response.json()
            distance = str(response['rows'][0]['elements'][0]['distance']['text'])
            distanceSplit = distance.split(" ")
            #print(distanceSplit)
            distance = 0.62137 * float(distanceSplit[0]) # converts km to miles
            distance = round(distance,2)
            travelTime = str(response['rows'][0]['elements'][0]['duration']['text'])
            #print(post.actualMileageVal, distance)
            post.actualMileageVal = distance
            #print(post.actualMileageVal, distance)
            post.save()
            #print("done")
        recommendedPosts = recommendedPosts.filter(actualMileageVal__lte=builderRange).order_by('actualMileageVal')


    return render(request, './homepage.html', {"posts":posts, "recommendedPosts":recommendedPosts, "recommendedBuilders":recommendedBuilders})

#@login_required
def dashboardView(request):
    posts = JobPost.objects.all()
    userprofile = request.user.userprofile

    form = JobForm()

    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            form.instance.userID = request.user
            API_KEY="<INSERT_API_KEY_HERE>"
            address = form.instance.location
            params = {
                'key':API_KEY,
                'address':address
            }
            base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
            response = requests.get(base_url, params=params).json()
            response.keys()

            if response['status'] == 'OK':
                #print(response)
                geometryObject = response['results'][0]['geometry']
                place_id = response['results'][0]['place_id']
                lat = geometryObject['location']['lat']
                lng = geometryObject['location']['lng']
                form.instance.placeID = place_id
                form.instance.lat = float(lat)
                form.instance.lng = float(lng)
                form.save()
                return redirect('dashboard')

            else:
                return redirect('dashboard') ##

    return render(request, './dashboard.html', {"form":form, "userprofile":userprofile, "posts":posts})

def postDetailView(request, post_id):
    post = JobPost.objects.get(pk=post_id)
    return render(request, './job_post.html', {'post':post})

def postOffersView(request, post_id):
    idData={'post_id':post_id}
    json.dumps(idData)
    return render(request, './job_post_offers.html', context={'idData':idData})


def conversationView(request, customer_id, builder_id):
    customer = User.objects.get(pk=customer_id)
    builder = User.objects.get(pk=builder_id)

    if Conversation.objects.filter(customer=customer, builder=builder).exists():
        conversation = Conversation.objects.get(customer=customer, builder=builder)
    else:
        conversation = Conversation.objects.create(customer=customer, builder=builder)
        conversation = Conversation.objects.get(customer=customer, builder=builder)

    if request.method == "POST":
        text = request.POST.get('message_text')

        if text:
            message = Messages.objects.create(text=text, convo=conversation, author=request.user.username)
            message.save()
            return redirect('conversation', customer_id=customer_id, builder_id=builder_id)

    return render(request, './conversation.html', {"conversation":conversation})

def postOfferView(request, post_id):
    post = JobPost.objects.get(pk=post_id)
    postOffers = post.offers.all()
    print(postOffers)
    form = OfferForm()
    createdOfferPost = False ## has this user created an offer on this post


    for x in postOffers:
        if x.user.id == request.user.id:
            createdOfferPost = True

    if createdOfferPost == False:

        if request.method == "POST":
            form = OfferForm(request.POST)

            if form.is_valid():
                form.save(commit=False)
                form.instance.post = post
                form.instance.user = request.user
                form.save()
                return redirect('dashboard')

    return render(request, './job_offer.html', {'form':form, 'createdOfferPost':createdOfferPost})

def baseView(request):
    return redirect('login')

def dashRedirectView(request):
    return redirect('dashboard')

def reviewView(request, job_id):
    form = ReviewForm()

    alreadyReviewed = False

    job = Job.objects.get(pk=job_id)
    if job.isReviewed:
        alreadyReviewed = True

    if request.method=="POST":
        form = ReviewForm(request.POST)
        job = Job.objects.get(pk=job_id)

        if form.is_valid():
            form.save(commit=False)
            form.instance.job = job
            form.instance.user = request.user
            total_rating = form.instance.punctuality + form.instance.timeliness + form.instance.satisfaction
            total_rating = total_rating/3
            form.instance.totalRating = total_rating
            form.save()
            job.isReviewed = True
            job.save()
            builderID = job.builder.userprofile.id
            builder = UserProfile.objects.get(pk=builderID)
            if builder.sumOfTotalRatings is None:
                num_ratings = 1
                builder.sumOfTotalRatings = total_rating
                builder.numOfRatings = num_ratings
                builder.avgRating = int(total_rating/num_ratings)
                builder.save()
            else:
                new_sum = builder.sumOfTotalRatings + total_rating
                builder.sumOfTotalRatings = new_sum
                num_ratings = builder.numOfRatings + 1
                builder.numOfRatings = num_ratings
                builder.avgRating = int(new_sum/num_ratings)
                builder.save()
            return redirect('dashboard')

    return render(request, './review.html', {"form":form, "alreadyReviewed":alreadyReviewed})
