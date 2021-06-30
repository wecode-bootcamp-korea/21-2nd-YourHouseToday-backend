import jwt
import json
import requests
from json.decoder import JSONDecodeError

from django.views import View
from django.http  import JsonResponse

from .models     import User
from .utils      import Mail, authorize_user
from my_settings import SECRET_KEY,ALGORITHM

class SingInView(View):
    def post(self,request):
        try:
            access_token = request.headers['Authorization']
            response     = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers = {'Authorization':f'Bearer {access_token}'}
            )

            if response.status_code != 200:
                return JsonResponse({'message':'INVALID TOKEN'}, status=401)
            
            user              = response.json()
            profile           = user['kakao_account']['profile']
            profile_image_url = profile['profile_image_url'] if profile['is_default_image'] == False else None

            result  = {
                'id'            : user['id'],
                'email'         : user['kakao_account']['email'],
                'nickname'      : profile['nickname'],
                'profile_image' : profile_image_url
            }
            
            if User.objects.filter(kakao_id=user['id']).exists():
                user = User.objects.get(kakao_id=user['id'])
                result['self_token'] = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)
                
            return JsonResponse(result, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

        except JSONDecodeError:
            return JsonResponse({'message':'JSON DECODE ERROR'}, status=200)
        
        except jwt.DecodeError:
            return JsonResponse({'message':'JWT DECODE ERROR'}, status=400)

        except ConnectionError:
            return JsonResponse({'message':'CONNECTION ERROR'}, status=400)

class NicknameCheckView(View):
    def post(self,request):
        try:
            nickname           = json.loads(request.body)['nickname']
           
            if User.objects.filter(nickname=nickname).exists():
                users        = list(User.objects.filter(nickname__istartswith=nickname))
                numbers      = list(map(lambda x: int(x.nickname.strip(nickname) or 0), users))
                new_nickname = nickname + str(max(numbers)+1)

                return JsonResponse({'message':'NICKNAME ALEADY EXISTS','recommend_nickname':new_nickname},status=400)

            return JsonResponse({'message':'SUCCESS'}, status=200)

        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

        except JSONDecodeError:
            return JsonResponse({'message':'JSON DECODE ERROR'}, status=400)

class SignUpView(View):
    def post(self,request):
        try:
            data       = json.loads(request.body)
            user       = User.objects.create(
                email         = data['email'],
                nickname      = data['nickname'],
                profile_image = data.get('profile_image'),
                kakao_id      = str(data['id'])
            )
            self_token = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)

            result = {
                'profile_image' : user.profile_image,
                'self_token'    : self_token    
            }

            signup_mail = Mail()
            signup_mail.create(
                receiver=data['email'],
                subject="Your House Today에 가입해주셔서 감사합니다!",
                template='mail_signup.html'
            )
            signup_mail.send()

            return JsonResponse(result, status=201)

        except KeyError:
            return JsonResponse({'message':'KEY ERROR'}, status=400)

        except JSONDecodeError:
            return JsonResponse({'message':'JSON DECODE ERROR'}, status=400)
        
        except jwt.DecodeError:
            return JsonResponse({'message':'JWT DECODE ERROR'}, status=400)

class AccountView(View):
    @authorize_user
    def get(self,request):
        result = {
            'postings' : [posting.image for posting in request.user.posting.all()],
            'likes'    : request.user.like.count()
        }
        return JsonResponse(result, status=200)