from django import forms
from django.forms import ModelForm
from .models import User, CHOICES1, JobPost, JobCategory, Offer, Job, Review, UserProfile

# store pass as hash w/ salt. this is done automatically through django's auth service.

class UserForm(ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class CategoriesForm(ModelForm):
    #jobCategory = forms.ModelMultipleChoiceField(queryset = JobCategory.objects.all(), label="Choose the job categories that you specialise in")
    class Meta:
        model = UserProfile
        exclude=['user','isCustomer', 'placeID', 'lat', 'lng', 'sumOfTotalRatings', 'avgRating', 'numOfRatings', 'actualMileageVal']
        labels={'jobCategory':"Choose category",
                'mileageRange':"Enter your preferred mileage range",
                'preferRating':"Please choose if you prefer Ratings or Proximity to be priotised",
                'location':"Enter your main location",
                } ## add the JS Google Maps AutoComplete code for this location field

    def __init__(self, *args, **kwargs):
        super(CategoriesForm, self).__init__(*args, **kwargs)
        self.fields['preferRating'].required = False

class BuilderCategoriesForm(ModelForm):
    #jobCategory = forms.ModelMultipleChoiceField(queryset = JobCategory.objects.all(), label="Choose the job categories that you specialise in")
    class Meta:
        model = UserProfile
        exclude=['user','isCustomer', 'placeID', 'lat', 'lng', 'sumOfTotalRatings', 'avgRating', 'numOfRatings', 'actualMileageVal', 'preferRating']
        labels={'jobCategory':"Choose category",
                'mileageRange':"Enter your preferred mileage range",
                'location':"Enter your main location",
                } ## add the JS Google Maps AutoComplete code for this location field

class JobForm(ModelForm):
    class Meta:
        model = JobPost
        exclude = ['userID', 'accepted', 'finished', 'lat', 'lng', 'placeID', 'actualMileageVal']
        labels = {
        'location':"Enter Job Location",
        'title':"Title",
        'description':"Description",
        'jobCategory':"Pick Category",
        'budget': "Enter your budget(£)",
        }

class OfferForm(ModelForm):
    class Meta:
        model = Offer
        exclude = ['post','user','isDeclined','isAccepted']
        labels = {
            'price':'Quoted Price',
            'comments': 'Add any comments'
        }

class ReviewForm(ModelForm): ## add in tool tips for each input field explaining each one. e.g. for punctuality just write did your builder show up on time everyday?
    class Meta:
        model = Review
        exclude =['job','user', 'totalRating']
        labels = {
            'punctuality':'Rate the punctuality of your builder from 1-5',
            'timeliness':'Rate the timeliness of your builder from 1-5',
            'satisfaction':'Rate your overall satisfaction from 1-5',
            'notes':'Enter any extra notes here'
        }


class PickCategoryForm(ModelForm):
    class Meta:
        model = JobCategory
        fields=['name']
        labels={
            'name':"Pick the job category you want to filter by"
        }