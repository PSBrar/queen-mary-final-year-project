from django.contrib import admin
from django.urls import path
from . import views
from . import api
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', views.loginView, name="login"),
    path('signup/', views.signupView, name="signup"),
    path('', views.baseView, name = "home"),
    path('homepage/<int:userID>/', views.homepageView, name = "homepage"),
    path('logout/', auth_views.LogoutView.as_view(template_name='./logout.html'), name='logout'),
    path('dashboard/', views.dashboardView, name="dashboard"),
    path('job_post/<int:post_id>/', views.postDetailView, name="jobpost"),
    path('job_offer/<int:post_id>/', views.postOfferView, name="joboffer"),
    path('job_offer_post/<int:post_id>/', views.postOffersView, name="joboffers"),
    path('conversation/<int:customer_id>/<int:builder_id>/', views.conversationView, name="conversation"),
    path('api/offer_decline_api/<int:offer_id>/', api.offer_decline_api, name = "offer_decline_api"),
    path('api/get_offers_api/<str:post_id>/', api.get_offers_api, name = "get_offers_api"),
    path('api/offer_accept_api/<int:offer_id>/<int:post_id>/', api.offer_accept_api, name = "offer_accept_api"),
    path('api/complete_job_api/<int:job_id>/', api.complete_job_api, name="complete_job_api"),
    path('api/dash_redirect_view', views.dashRedirectView, name="dash_redirect_view"),
    path('review/<int:job_id>/', views.reviewView, name = "review"),
    path('profile_settings/', views.addCategoriesView, name="add_categories")

]
