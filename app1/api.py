from django.http import JsonResponse
from .models import Offer, JobPost, Job
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.http.response import HttpResponseBadRequest

def offer_decline_api(request, offer_id):
    if request.method == "PUT":
        #print("works")
        offer = get_object_or_404(Offer, pk=offer_id)
        offer.isDeclined = True
        offer.save()
        return JsonResponse({})
    else:
        return HttpResponseBadRequest("Invalid method")

def offer_accept_api(request, offer_id, post_id):
    if request.method == "PUT":
        #print("works")
        offer = get_object_or_404(Offer, pk=offer_id)
        post = get_object_or_404(JobPost, pk=post_id)
        post.accepted = True
        post.save()
        offer.isAccepted = True
        offer.save()
        job = Job.objects.create(offer=offer, post=post, customer=request.user, builder=offer.user)
        #job.save()
        return JsonResponse({})
        #return redirect('dashboard')
    else:
        return HttpResponseBadRequest("Invalid method")        

def get_offers_api(request, post_id):
    print(post_id)
    #print("api call recieved")
    post = JobPost.objects.get(pk=post_id)

    return JsonResponse({
        'offers': [
            offer.to_dict()
            for offer in post.offers.all()
        ]
    })

def complete_job_api(request, job_id):
    if request.method == "PUT":
        print("api reach")
        job = get_object_or_404(Job, pk=job_id)
        job.isOngoing = False
        job.save()
        print("working")
        return JsonResponse({})
    else:
        return HttpResponseBadRequest("Invalid method")