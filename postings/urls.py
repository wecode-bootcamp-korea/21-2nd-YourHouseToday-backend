from django.urls import path

from postings.views import PostingsView, PostingView, LikeView

urlpatterns = [
    path('', PostingsView.as_view()),
    path('/<int:posting_id>', PostingView.as_view()),
    path('/like/<int:posting_id>', LikeView.as_view())
]
