from django.urls import path

from postings.views import PictureListView, PostingView, LikeView

urlpatterns = [
    path('', PictureListView.as_view()),
    path('/<int:posting_id>', PostingView.as_view()),
    path('/like/<int:posting_id>', LikeView.as_view())
]
