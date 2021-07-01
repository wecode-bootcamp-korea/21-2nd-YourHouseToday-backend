from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('postings', include('postings.urls')),
    path('users', include('users.urls')),
    path('comments', include('comments.urls'))

]
