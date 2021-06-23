from django.urls import path

from postings.views import PictureListView

urlpatterns = [
    path('',PictureListView.as_view()),
]
