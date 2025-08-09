from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

# Create your models here.

CHOICES1 = (
    ('Ratings', 'Ratings'),
    ('Proximity', 'Proximity'),
    )


class User(AbstractUser):
    pass

    def __str__(self):
        return self.username


class JobCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    isCustomer = models.BooleanField(default=False)
    jobCategory = models.ForeignKey(JobCategory, null=True, on_delete=models.DO_NOTHING)
    #jobCategory = models.ManyToManyField(JobCategory, blank=True, symmetrical=False)
    placeID = models.CharField(max_length = 250, null=True)
    location = models.CharField(max_length=100, null=True)
    mileageRange = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    sumOfTotalRatings = models.IntegerField(default=0)
    avgRating = models.IntegerField(default=0)
    numOfRatings = models.IntegerField(default=0)
    preferRating = models.CharField(max_length=50, choices=CHOICES1, null=True, blank=True)
    actualMileageVal = models.FloatField(default=0)

User.userprofile = property(lambda u:UserProfile.objects.get_or_create(user=u)[0])


class Conversation(models.Model):
    customer = models.ForeignKey(User, related_name="convo", on_delete=models.DO_NOTHING)
    builder = models.ForeignKey(User, related_name="my_convo", on_delete=models.DO_NOTHING)

class JobPost(models.Model):
    userID = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    budget = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    jobCategory = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    ##jobCategory = models.ManyToManyField('JobCategory', blank=False, symmetrical=False)
    accepted = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    placeID = models.CharField(max_length = 250, null=True)
    location = models.CharField(max_length=100)
    actualMileageVal = models.FloatField(default=0)


class Offer(models.Model):
    post = models.ForeignKey(JobPost, related_name="offers", on_delete=models.CASCADE)
    price = models.IntegerField()
    comments = models.TextField()
    user = models.ForeignKey(User, related_name="offers", on_delete=models.CASCADE) # this should always be a builder user.
    isAccepted = models.BooleanField(default=False)
    isDeclined = models.BooleanField(default=False)


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.post.id,
            'price': self.price,
            'comments': self.comments,
            'user': self.user.username,
            'isAccepted': self.isAccepted,
            'isDeclined': self.isDeclined,
            'msgURL': reverse('conversation', kwargs={'customer_id': self.post.userID.id, 'builder_id': self.user.id}),
            'declineAPI': reverse('offer_decline_api', kwargs={'offer_id': self.id}),
            'acceptAPI': reverse('offer_accept_api', kwargs={'offer_id': self.id, 'post_id':self.post.id})
        }

class Messages(models.Model):
    text = models.TextField()
    convo = models.ForeignKey(Conversation, related_name="msgs", on_delete=models.CASCADE, null=True) 
    author = models.TextField(default="") 
    created = models.DateTimeField(auto_now_add=True)

class Job(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    offer = models.OneToOneField(Offer, related_name='jobs', on_delete=models.DO_NOTHING)
    post = models.OneToOneField(JobPost, related_name='jobs', on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(User, related_name='customer_jobs', on_delete=models.DO_NOTHING) ## this user is the customer
    isOngoing = models.BooleanField(default=True)
    isReviewed = models.BooleanField(default=False)
    builder = models.ForeignKey(User, related_name='builder_jobs', on_delete=models.DO_NOTHING)


class Review(models.Model):
    job = models.OneToOneField(Job, related_name="reviews", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.DO_NOTHING) ##customer
    notes = models.TextField()
    punctuality = models.IntegerField()
    timeliness = models.IntegerField()
    satisfaction = models.IntegerField()
    totalRating = models.IntegerField()
