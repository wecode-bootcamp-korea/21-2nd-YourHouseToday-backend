import math, json, datetime, boto3, uuid

from django.views     import View
from django.db.models import Q
from django.http      import JsonResponse

from .models      import Posting, Like, HousingType, Size, Style, Color
from users.utils  import authorize_user
from my_settings  import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_CUSTOM_DOMAIN, AWS_STORAGE_BUCKET_NAME

class PostingsView(View):
    def get(self, request):
        housing_type  = request.GET.get('housing-type', None)
        back_color    = request.GET.get('back-color', None)
        item_color    = request.GET.get('item-color', None)
        min_size      = int(request.GET.get('min-size', 1))
        max_size      = int(request.GET.get('max-size', 71))
        style         = request.GET.get('style', None)
        sort          = request.GET.get('sort', 'create_at')
        limit         = int(request.GET.get('limit', 8))
        offset        = int(request.GET.get('offset',1))
        postings_list = []

        offset = limit*(offset-1)

        if not max_size%10:
            max_size -= 1

        min_size = math.ceil(min_size/10)
        max_size = math.ceil(max_size/10)

        q = Q()

        if housing_type:
            q &= Q(housing_type_id=housing_type)

        if back_color:
            q &= Q(back_color_id=back_color)

        if item_color:
            q &= Q(item_color_id=item_color)
        
        if style:
            q &= Q(style_id=style)
        
        q &= Q(size__id__range=(min_size,max_size))
        
        postings = Posting.objects.filter(q).order_by(sort)[offset:offset+limit]
        
        postings_list = [
            {
                'id'             : posting.id,
                'profileImage'   : posting.user.profile_image,
                'profileName'    : posting.user.nickname,
                'introduce'      : posting.user.introduction,
                'title'          : posting.text,
                'cardImage'      : posting.image,
                'viewCount'      : posting.view,
                'heartCount'     : posting.like_posting.count(),
                'commentCount'   : posting.comment_set.order_by('create_at').count(),
                'writerImage'    : [posting.comment_set.order_by('create_at')[0].user.profile_image] if posting.comment_set.count() != 0 else '',
                'writerName'     : [posting.comment_set.order_by('create_at')[0].user.nickname] if posting.comment_set.count() != 0 else '',
                'commentContent' : [posting.comment_set.order_by('create_at')[0].text] if posting.comment_set.count() != 0 else ''
            }
            for posting in postings]
        return JsonResponse({'result':postings_list}, status = 200)

    @authorize_user
    def post(self, request):
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            image = request.FILES['image']
            my_uuid = str(uuid.uuid4())
            s3_client.upload_fileobj(
                image, 
                AWS_STORAGE_BUCKET_NAME,
                my_uuid,
                ExtraArgs={
                    "ContentType": image.content_type
                })
            image_url    = AWS_S3_CUSTOM_DOMAIN + my_uuid
            data         = json.loads(request.POST['info'])
            housing_type = HousingType.objects.get(type=data['housing_type'])
            size         = Size.objects.get(type=data['size'])
            style        = Style.objects.get(type=data['style'])
            back_color   = Color.objects.get(type=data['back_color'])
            item_color   = Color.objects.get(type=data['item_color'])
            text         = data['text']

            Posting.objects.create(
                user         = request.user,
                housing_type = housing_type,
                size         = size,
                style        = style,
                back_color   = back_color,
                item_color   = item_color,
                image        = image_url,
                text         = text,
                update_at    = datetime.datetime.now()
                )
            return JsonResponse({"messege":"SUCCESS"}, status = 201)

        except KeyError:
            return JsonResponse({"messege":"KEY_ERROR"}, status = 400)

class PostingView(View):
    def get(self, request, posting_id):
        try:
            posting = Posting.objects.get(id=posting_id)
            posting.view += 1
            posting.save()
            result = {
                'id'           : posting.id,
                'image'        : posting.image,
                'text'         : posting.text,
                'size'         : posting.size.type,
                'style'        : posting.style.type,
                'like'         : posting.like_posting.count(),
                'housing_type' : posting.housing_type.type,
                'view'         : posting.view,
                'related_user' : [{  
                    'id'           : posting.user.id,
                    'nickname'     : posting.user.nickname,
                    'image_url'    : posting.user.profile_image,
                    'introduction' : posting.user.introduction   
                }]
            }
            
            return JsonResponse({'posting' : result}, status=200)
        except Posting.DoesNotExist:
            return JsonResponse({'message': 'object does not exist'}, status=404)
      
class LikeView(View):    
    @authorize_user
    def post(self, request, posting_id):
        user = request.user
        
        Like.objects.create(
                user_id    = user.id,
                posting_id = posting_id
            )
        
        return JsonResponse({'message':'CREATE_LIKE'}, status=201)
         
    @authorize_user
    def delete(self, request, posting_id):
        user = request.user
        
        Like.objects.get(
            user_id    = user.id,
            posting_id = posting_id
            ).delete()
        return JsonResponse({'message': 'DELETE_LIKE'}, status=204)
