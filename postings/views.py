import math

from django.views     import View
from django.db.models import Q
from django.http      import JsonResponse

from postings.models import Posting

class PictureListView(View):
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
                'writerImage'    : posting.comment_set.order_by('create_at')[0].user.profile_image,
                'writerName'     : posting.comment_set.order_by('create_at')[0].user.nickname,
                'commentContent' : posting.comment_set.order_by('create_at')[0].text
            }
            for posting in postings]
        return JsonResponse({'result':postings_list}, status = 200)