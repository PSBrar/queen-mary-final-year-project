from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app1.models import *

class JobPostAdmin(admin.ModelAdmin):
    pass

class JobCategoryAdmin(admin.ModelAdmin):
    pass        

class UserProfileAdmin(admin.ModelAdmin):
    pass

class OfferAdmin(admin.ModelAdmin):
    pass

class MessagesAdmin(admin.ModelAdmin):
    pass

class JobsAdmin(admin.ModelAdmin):
    pass    

class ReviewAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)
admin.site.register(JobPost, JobPostAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(Job, JobsAdmin)
admin.site.register(Review, ReviewAdmin)

