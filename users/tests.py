import jwt
import json
import datetime
from unittest.mock        import patch, MagicMock

from django.http.response import JsonResponse
from django.test          import TestCase, Client
from django.test.client   import RequestFactory

from .models         import User
from .utils          import authorize_user,sort_user
from postings.models import Posting, HousingType, Style, Size, Color, Like
from my_settings     import SECRET_KEY,ALGORITHM

class SignInTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연",
            email         = "anne_with_an_e@kakao.com"
        )

    @patch("users.views.requests")
    def test_kakao_signin_success_existing_user(self,mocked_requests):
        class MockedResponse:
            status_code = 200

            def json(self):
                return {                  
                    "id":1111111111,
                    "kakao_account": { 
                        "profile_needs_agreement": False,
                        "profile": {
                            "nickname"           : "정연",
                            "thumbnail_image_url": "http://profile_image.jpg",
                            "profile_image_url"  : "http://profile_image.jpg",
                            "is_default_image"   : False
                        },
                        "email_needs_agreement"  : False,
                        "is_email_valid"         : True,  
                        "is_email_verified"      : True,   
                        "email"                  : "jyeon@kakao.com"
                    }
                }

        mocked_requests.get           = MagicMock(return_value=MockedResponse())
        response                      = Client().post('/users/signin', HTTP_AUTHORIZATION='access_token')
        response.json()['self_token'] = 'self_token'

        self.assertEqual(
            response.json(),
            {
                'id'            : 1111111111,
                'profile_image' : "http://profile_image.jpg",
                'nickname'      : "정연",
                'email'         : "jyeon@kakao.com",
                'self_token'    : 'self_token'
            }
        )
        self.assertEqual(
            response.status_code,200
        )
        
    @patch("users.views.requests")
    def test_kakao_signin_success_new_user(self,mocked_requests):     
        class MockedResponse:
            status_code = 200

            def json(self):
                return {                  
                    "id":2222222222,
                    "kakao_account": { 
                        "profile_needs_agreement": False,
                        "profile": {
                            "nickname"           : "명준",
                            "thumbnail_image_url": "http://profile_image.jpg",
                            "profile_image_url"  : "http://profile_image.jpg",
                            "is_default_image"   : False
                        },
                        "email_needs_agreement"  : False,
                        "is_email_valid"         : True,  
                        "is_email_verified"      : True,   
                        "email"                  : "mjoon@kakao.com"
                    }
                }
        
        mocked_requests.get  = MagicMock(return_value=MockedResponse())
        response             = Client().post('/users/signin', HTTP_AUTHORIZATION='access_token')

        self.assertEqual(
            response.json(),
            {
                'id'            : 2222222222,
                'profile_image' : "http://profile_image.jpg",
                'nickname'      : "명준",
                'email'         : "mjoon@kakao.com",
            }
        )
        self.assertEqual(
            response.status_code,200
        )

    @patch("users.views.requests")
    def test_kakao_signin_success_new_user_no_profile_image(self,mocked_requests):
        class MockedResponse:
            status_code = 200

            def json(self):
                return {                  
                    "id":2222222222,
                    "kakao_account": { 
                        "profile_needs_agreement": False,
                        "profile": {
                            "nickname"           : "명준",
                            "thumbnail_image_url": "http://profile_image.jpg",
                            "profile_image_url"  : "http://profile_image.jpg",
                            "is_default_image"   : True
                        },
                        "email_needs_agreement"  : False,
                        "is_email_valid"         : True,  
                        "is_email_verified"      : True,   
                        "email"                  : "mjoon@kakao.com"
                    }
                }

        mocked_requests.get = MagicMock(return_value=MockedResponse())
        response            = Client().post('/users/signin', HTTP_AUTHORIZATION='access_token')

        self.assertEqual(
            response.json(),
            {
                'id'            : 2222222222,
                'profile_image' : None,
                'nickname'      : "명준",
                'email'         : "mjoon@kakao.com",
            }
        )
        self.assertEqual(
            response.status_code,200
        )

    @patch("users.views.requests")
    def test_kakao_signin_error_is_response_from_kakao(self,mocked_requests):
        class MockedResponse:
            status_code = 400

            def json(self):
                return {                  
                "error" :"error",
                "error_discription" : "error_dirscription",
                "error_code" : "error_code"
                }
        
        mocked_requests.get = MagicMock(return_value=MockedResponse())
        response            = Client().post('/users/signin', HTTP_AUTHORIZATION='access_token')

        self.assertEqual(
            response.json(),
            {'message':'INVALID TOKEN'}
        )
        self.assertEqual(
            response.status_code,401
        )

    @patch("users.views.requests")
    def test_kakao_signin_key_error(self,mocked_requests):

        class MockedResponse():
            status_code = 200

            def json(self):
                return {}
        
        mocked_requests.get = MagicMock(return_value=MockedResponse())
        response            = Client().post('/users/signin', HTTP_AUTHORIZATION='access_token')

        self.assertEqual(
            response.json(),
            {'message':'KEY ERROR'}
        )
        self.assertEqual(
            response.status_code,400
        )

class NicknameCheckTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연",
            email         = "jyeon@kakao.com"
        )

        User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연10",
            email         = "jyeon@kakao.com"
        )

        User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연20",
            email         = "jyeon@kakao.com"
        )

    def test_nickname_check_if_unique(self):
        nickname = '명준'
        response = Client().post(
            '/users/nickname-check',
            {'nickname':nickname},
            content_type='application/json'
        )

        self.assertEqual(
            response.json(),
            {'message':'SUCCESS'}
        )
        self.assertEqual(
            response.status_code, 200
        )

    def test_nickname_check_if_not_unique(self):
        nickname     = '정연'
        response     = Client().post(
            '/users/nickname-check', 
            {'nickname':nickname},
            content_type='application/json'
        )
        response.json()['recommend_nickname'] = '정연10'

        self.assertEqual(
            response.json(),
            {'message':'NICKNAME ALEADY EXISTS', 'recommend_nickname': '정연10'}
        )
        self.assertEqual(
            response.status_code, 400
        )

    def test_nickname_check_key_error(self):
        response     = Client().post(
            '/users/nickname-check',
            content_type='application/json'
        )

        self.assertEqual(
            response.json(),
            {'message':'KEY ERROR'}
        )
        self.assertEqual(
            response.status_code, 400
        )

    def test_nickname_json_decode_error(self):
        response     = Client().post('/users/nickname-check')

        self.assertEqual(
            response.json(),
            {'message':'JSON DECODE ERROR'}
        )
        self.assertEqual(
            response.status_code, 400
        )

class SignUpTest(TestCase):
    def test_sign_up_success(self):
        data = {
            'email':'email',
            'nickname':'nickname',
            'profile_image':'profile_image',
            'id':'kakao_id'
        }    
        response = Client().post('/users/signup', data, content_type='application/json')    
        response.json()['self_token'] = 'self_token'

        self.assertEqual(
            response.json(),
            {
                'profile_image' : "profile_image",
                'self_token'    : 'self_token'
            }
        )
        self.assertEqual(
            response.status_code, 201
        )

    def test_sign_up_key_error(self):
        response = Client().post('/users/signup', {}, content_type='application/json')

        self.assertEqual(
            response.json(),
            {'message':'KEY ERROR'}
        )
        self.assertEqual(
            response.status_code, 400
        )

    def test_sign_up_json_decode_error(self):
        data = {}    
        response = Client().post('/users/signup', data)

        self.assertEqual(
            response.json(),
            {'message':'JSON DECODE ERROR'}
        )
        self.assertEqual(
            response.status_code, 400
        )

class AuthorizseUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연",
            email         = "jyeon@kakao.com"
        )
        cls.token = jwt.encode({'id':cls.user.id},SECRET_KEY,ALGORITHM)
    
    def test_authorize_user_decorator_success(self):
        @authorize_user
        def mocked_view(self,request):
            return request.user.id

        request  = RequestFactory().get('', HTTP_AUTHORIZATION=AuthorizseUserTest.token)
        response = mocked_view(self,request)
        
        self.assertEqual(
            response,
            AuthorizseUserTest.user.id
        )

    def test_authorize_user_decorator_invalid_user(self):
        @authorize_user
        def mocked_view(self,request):
            return request.user.id

        token = jwt.encode({'id':'2'},SECRET_KEY,ALGORITHM)
        request  = RequestFactory().get('', HTTP_AUTHORIZATION=token)
        response = mocked_view(self,request)
        
        self.assertEqual(
            response.content.decode('utf-8'),
            '{"message": "INVALID USER"}'
        )
        self.assertEqual(
            response.status_code, 401
        )


    def test_authorize_user_decorator_jwt_decode_error(self):
        @authorize_user
        def mocked_view(self,request):
            return request.user.id

        request  = RequestFactory().get('', HTTP_AUTHORIZATION='wrong_token')
        response = mocked_view(self,request)

        self.assertEqual(
            response.content.decode('utf-8'),
            '{"message": "JWT DECODE ERROR"}'
        )
        self.assertEqual(
            response.status_code, 401
        )

    def test_authorize_user_decorator_key_error(self):
        @authorize_user
        def mocked_view(self,request):
            return request.user.id

        request  = RequestFactory().get('')
        response = mocked_view(self,request)

        self.assertEqual(
            response.content.decode('utf-8'),
            '{"message": "KEY ERROR"}'
        )
        self.assertEqual(
            response.status_code, 401
        )

class SortUserTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연",
            email         = "jyeon@kakao.com"
        )
        cls.token = jwt.encode({'id':cls.user.id},SECRET_KEY,ALGORITHM)

    
    def test_sort_user_decorator_user(self):
        @sort_user
        def mocked_view(self,request):
            if hasattr(request,'user'):
                return request.user
            return None

        request  = RequestFactory().get('', HTTP_AUTHORIZATION=SortUserTest.token)
        response = mocked_view(self,request)
        
        self.assertEqual(
            response,
            SortUserTest.user
        )

    def test_sort_user_decorator_non_user(self):
        @sort_user
        def mocked_view(self,request):
            if hasattr(request,'user'):
                return request.user
            return None

        request  = RequestFactory().get('')
        response = mocked_view(self,request)
        
        self.assertEqual(
            response,
            None
        )

    def test_sort_user_decorator_jwt_decode_error(self):
        @sort_user
        def mocked_view(self,request):
            return request.user.id

        request  = RequestFactory().get('', HTTP_AUTHORIZATION='wrong_token')
        response = mocked_view(self,request)

        self.assertEqual(
            response.content.decode('utf-8'),
            '{"message": "JWT DECODE ERROR"}'
        )
        self.assertEqual(
            response.status_code, 401
        )

class AccountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            kakao_id      = "1111111111",
            profile_image = "http://profile_image.jpg",
            nickname      = "정연",
            email         = "anne_with_an_e@kakao.com"
        )

        color = Color.objects.create(type="test")
        housing = HousingType.objects.create(type="test")
        size = Size.objects.create(type="test")
        style = Style.objects.create(type="test")

        p1 = Posting.objects.create(
            user=user, image="1.jpg",
            text="text",
            back_color=color,housing_type=housing,item_color=color,size=size,style=style,
            update_at=datetime.datetime.now()
        )
        p2 = Posting.objects.create(
            user=user, image="2.jpg",
            text="text",
            back_color=color,housing_type=housing,item_color=color,size=size,style=style,
            update_at=datetime.datetime.now()
        )
        p3 = Posting.objects.create(
            user=user, image="3.jpg",
            text="text",
            back_color=color,housing_type=housing,item_color=color,size=size,style=style,
            update_at=datetime.datetime.now()
        )

        Like.objects.create(posting=p1, user=user)
        Like.objects.create(posting=p2, user=user)
        Like.objects.create(posting=p3, user=user)


    def test_mypage_success(self):
        user     = User.objects.get(kakao_id="1111111111")
        token    = jwt.encode({'id': user.id}, SECRET_KEY, ALGORITHM)
        response = Client().get('/users', HTTP_AUTHORIZATION=token)

        self.assertEqual(
            response.json(),
            {
                "postings" : ['1.jpg','2.jpg','3.jpg'],
                "likes"    : 3
            }
        )
        self.assertEqual(
            response.status_code, 200
        )