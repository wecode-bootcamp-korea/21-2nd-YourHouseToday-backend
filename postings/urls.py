from django.urls import path

from postings.views import PictureListView, PostingView

urlpatterns = [
    path('', PictureListView.as_view()),
    path('/<int:posting_id>', PostingView.as_view())
]
