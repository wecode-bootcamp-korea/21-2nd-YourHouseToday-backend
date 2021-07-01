import json, jwt

from unittest.mock      import patch, MagicMock
from django.test        import TestCase, Client
from django.core.files  import File

from postings.models import Posting, HousingType, Style, Size, Color, Like
from users.models    import User
from comments.models import Comment
from my_settings import SECRET_KEY, ALGORITHM

class PostingsViewTest(TestCase):
    def setUp(self):
        posting_user = User.objects.create(
            id            = 1,
            email         = 'asdf@naver.com', 
            nickname      = 'wecode', 
            kakao_id      = '1', 
            introduction  = 'hello wecode', 
            profile_image = 'profile_image_url'
            )
        comment_user = User.objects.create(
            id            = 2,
            email         = '1234@naver.com', 
            nickname      = '아이언맨', 
            kakao_id      = '2', 
            introduction  = 'hi wecode', 
            profile_image = 'profile_image_url'
            )
        housing_type_one_room = HousingType.objects.create(id=1, type='one_room')
        housing_type_apart    = HousingType.objects.create(id=2, type='apartment')
        style_modern          = Style.objects.create(id=1, type='modern')
        style_classic         = Style.objects.create(id=2, type='classic')
        item_color_red        = Color.objects.create(id=1, type='red')
        item_color_blue       = Color.objects.create(id=2, type='blue')
        back_color_black      = Color.objects.create(id=3, type='black')
        back_color_white      = Color.objects.create(id=4, type='white')
        size_10   = Size.objects.create(id=1, type='10')
        size_20   = Size.objects.create(id=2, type='20')
        posting_1 = Posting.objects.create(
            id           = 1,
            user         = posting_user,
            housing_type = housing_type_one_room,
            size         = size_10,
            style        = style_modern,
            item_color   = item_color_red,
            back_color   = back_color_black,
            image        = 'posting_image_url',
            text         = '너무 이쁜집',
            update_at    = '2020-12-11',
            view         = 10
            )
        posting_2 = Posting.objects.create(
            id           = 2,
            user         = posting_user,
            housing_type = housing_type_apart,
            size         = size_20,
            style        = style_classic,
            item_color   = item_color_blue,
            back_color   = back_color_white,
            image        = 'posting_image_url',
            text         = '너무 이쁜집',
            update_at    = '2021-10-20',
            view         = 20
            )
        Posting.objects.create(
            id           = 3,
            user         = posting_user,
            housing_type = housing_type_apart,
            size         = size_10,
            style        = style_classic,
            item_color   = item_color_blue,
            back_color   = back_color_black,
            image        = 'posting_image_url',
            text         = '제 방을 소개합니다',
            update_at    = '2021-10-25',
            view         = 11
            )
        Posting.objects.create(
            id           = 4,
            user         = posting_user,
            housing_type = housing_type_one_room,
            size         = size_20,
            style        = style_modern,
            item_color   = item_color_red,
            back_color   = back_color_white,
            image        = 'posting_image_url',
            text         = '자랑합니다',
            update_at    = '2019-09-20',
            view         = 24
            )
        Comment.objects.create(id=1, posting=posting_1, user=comment_user, text='너무 이쁘네요')
        Comment.objects.create(id=2, posting=posting_2, user=comment_user, text='너무 보기 좋아요')
        Like.objects.create(id=1, user=comment_user, posting=posting_1)
        Like.objects.create(id=2, user=comment_user, posting=posting_2)
    
    def tearDown(self):
        User.objects.all().delete()
        HousingType.objects.all().delete()
        Style.objects.all().delete()
        Size.objects.all().delete()
        Color.objects.all().delete()
        Posting.objects.all().delete()
        Like.objects.all().delete()

    def test_postings_list_get_success(self):
        client   = Client()
        response = client.get('/postings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'result': 
            [
                {
                    'id': 1, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 10, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 이쁘네요']
                },
                {
                    'id': 2, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 20, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 보기 좋아요']
                },
                {
                    'id': 3, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '제 방을 소개합니다', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 11, 
                    'heartCount': 0, 
                    'commentCount': 0, 
                    'writerImage': '', 
                    'writerName': '', 
                    'commentContent': ''
                },
                {
                    'id': 4, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '자랑합니다', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 24, 
                    'heartCount': 0, 
                    'commentCount': 0, 
                    'writerImage': '', 
                    'writerName': '', 
                    'commentContent': ''
                }

            ]
        })
        
    def test_postings_list_filter_success(self):
        client   = Client()
        response = client.get('/postings?style=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'result': 
            [
                {
                    'id': 2, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 20, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 보기 좋아요']
                },
                {
                    'id': 3, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '제 방을 소개합니다', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 11, 
                    'heartCount': 0, 
                    'commentCount': 0, 
                    'writerImage': '', 
                    'writerName': '', 
                    'commentContent': ''
                }
            ]
        })
        
    def test_postings_list_order_by_success(self):
        client   = Client()
        response = client.get('/postings?sort=-view')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'result': 
            [
                {
                    'id': 4, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '자랑합니다', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 24, 
                    'heartCount': 0, 
                    'commentCount': 0, 
                    'writerImage': '', 
                    'writerName': '', 
                    'commentContent': ''
                },
                {
                    'id': 2, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 20, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 보기 좋아요']
                },
                {
                    'id': 3, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '제 방을 소개합니다', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 11, 
                    'heartCount': 0, 
                    'commentCount': 0, 
                    'writerImage': '', 
                    'writerName': '', 
                    'commentContent': ''
                },
                {
                    'id': 1, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 10, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 이쁘네요']
                }
            ]
        })
        
    def test_postings_list_page_get(self):
        client   = Client()
        response = client.get('/postings?limit=2&offset=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'result': 
            [
                {
                    'id': 1, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 10, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 이쁘네요']
                },
                {
                    'id': 2, 
                    'profileImage': 'profile_image_url', 
                    'profileName': 'wecode', 
                    'introduce': 'hello wecode', 
                    'title': '너무 이쁜집', 
                    'cardImage': 'posting_image_url', 
                    'viewCount': 20, 
                    'heartCount': 1, 
                    'commentCount': 1, 
                    'writerImage': ['profile_image_url'], 
                    'writerName': ['아이언맨'], 
                    'commentContent': ['너무 보기 좋아요']
                }
            ]
        })
    @patch('postings.views.boto3.client')
    def test_writing_success(self, mock_s3client):
        client        = Client()
        mock_img      = MagicMock(sepc=File)
        mock_img.name = 'img.jpg'
        mock_s3client.upload_fileobj = MagicMock()
        access_token                 = jwt.encode({'id': 1}, SECRET_KEY, ALGORITHM)
        headers                      = {'HTTP_Authorization': access_token}
        form_data = {
            'image': mock_img,
            'info' : json.dumps({
                'housing_type' : 'one_room',
                'size'         : '10',
                'style'        : 'modern',
                'back_color'   : 'black',
                'item_color'   : 'red',
                'text'         : 'test'
                })}
        response = client.post('/postings', form_data, **headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"messege":"SUCCESS"})

class PostingTestCase(TestCase): 
    def setUp(self):
        posting_user = User.objects.create(
            id            = 1,
            email         = 'asdf@naver.com',
            nickname      = '하이',
            kakao_id      = 1,
            introduction  = '안녕하세요',
            profile_image = 'profile_image_url'
            )
        size_30 = Size.objects.create(id=1, type='30')
        style_modern = Style.objects.create(id=1, type='modern')
        housing_type_one_room = HousingType.objects.create(id=1, type='one_room')
        color = Color.objects.create(id=1,type='red')
        posting_1 = Posting.objects.create(
            id        = 1,
            item_color = color,
            back_color = color,
            user      = posting_user,
            size      = size_30,
            style     = style_modern,
            housing_type   = housing_type_one_room,
            image     = 'posting_image_url',
            text      = '굿굿',
            update_at = '2021-06-28',
            view      = 150
        )
        posting_comment_user = User.objects.create(
            id            = 2,
            email         = 'a12f@naver.com',
            nickname      = '하이!!',
            kakao_id      = 2,
            introduction  = '안녕하세요!!',
            profile_image = 'profile_image_url'
            )
        posting_like = Like.objects.create(
            id      = 1,
            user    = posting_comment_user,
            posting = posting_1
        )
        Comment.objects.create(id=1, posting=posting_1, user=posting_comment_user, text='너무 이쁘다')
        
    def tearDown(self):
        Posting.objects.all().delete()
        Comment.objects.all().delete()
        Like.objects.all().delete()
    def test_postingview_get_success(self):  
        client   = Client()  
        response = client.get('/postings/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'posting' :
                {
                'id'          : 1,
                'image'       : "posting_image_url",
                'text'        : "굿굿",
                'size'        : '30',
                'style'       : 'modern',
                'like'        : 1,
                'housing_type': 'one_room', 
                'view'        : 151,
                'related_user' : [{  
                    'id'           : 1,
                    'nickname'     : '하이',
                    'image_url'    : 'profile_image_url',
                    'introduction' : '안녕하세요'
                    }]
                }
        })