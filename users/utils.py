import jwt
import json
import requests
from json.decoder import JSONDecodeError

from django.http import JsonResponse

from .models     import User
from my_settings import SECRET_KEY, ALGORITHM

def authorize_user(func):
    def wrapper(self,request, **kwarg):
        try:
            self_token = request.headers['Authorization']    
            payload    = jwt.decode(self_token, SECRET_KEY, ALGORITHM)

            if not User.objects.filter(id=payload['id']).exists():
                return JsonResponse({'message' : 'INVALID USER'}, status=401)

            request.user = User.objects.get(id=payload['id'])

        except KeyError:
            return JsonResponse({'message' : 'KEY ERROR'},status=401)     

        except jwt.DecodeError:
            return JsonResponse({'message' : 'JWT DECODE ERROR'},status=401)

        return func(self,request,**kwarg)

    return wrapper

def sort_user(func):
    def wrapper(self,request):
        try:
            self_token = request.headers.get('Authorization')

            if self_token == None:
                return func(self,request)

            payload    = jwt.decode(self_token, SECRET_KEY, ALGORITHM)

            if not User.objects.filter(id=payload['id']).exists():
                return JsonResponse({'message':'INVALID USER'}, status=401)

            request.user = User.objects.get(id=payload['id'])

        except jwt.DecodeError:
            return JsonResponse({'message':'JWT DECODE ERROR'},status=401)

        return func(self,request)

    return wrapper