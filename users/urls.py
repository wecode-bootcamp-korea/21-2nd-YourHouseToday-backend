from django.urls import path
from .views      import AccountView, SingInView, NicknameCheckView, SignUpView

urlpatterns = [
    path('/signin',SingInView.as_view()),
    path('/nickname-check',NicknameCheckView.as_view()),
    path('/signup',SignUpView.as_view()),
    path('',AccountView.as_view())

]
