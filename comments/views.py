import json

from django.http  import JsonResponse
from django.views import View

from .models         import Comment
from postings.models import Posting
from users.utils     import authorize_user

class CommentView(View):
    @authorize_user
    def post(slef, request):
        try:
            posting_id = int(request.GET.get('posting_id'))
            data       = json.loads(request.body)  
            
            if not Posting.objects.filter(id = posting_id).exists():
                return JsonResponse({'message': 'INVALID_POSTING_ID'}, status=400)
            
            Comment.objects.create(
            text       = data['text'], 
            user       = request.user,
            posting_id = posting_id
            )
            return JsonResponse({'message': 'CREATED'}, status=201) 
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEY_ERROR'}, status=400)
        
    def get(self, request):
        try:        
            posting_id = int(request.GET.get('posting_id', 0))
            limit      = int(request.GET.get('limit', 5))
            offset     = int(request.GET.get('offset',1))
            offset     = limit*(offset-1)
            comments = list(Comment.objects.filter(posting_id=posting_id).order_by('-create_at'))[offset:offset+limit]
            result = [{
                'id'            : comment.id,
                'text'          : comment.text,
                'create_at'     : str(comment.create_at)[:10],
                'user_id'       : comment.user.id,
                'user_nickname' : comment.user.nickname,
                'user_profile'  : comment.user.profile_image
                }for comment in comments]
            
            return JsonResponse({'comment' : result}, status=200)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
    
    @authorize_user 
    def patch(self, request, comment_id):
        try:
            data = json.loads(request.body)
            comment = Comment.objects.get(id=comment_id)
            comment.text = data['text']
            comment.save()
            
            return JsonResponse({'message': 'COMMENT_PATCH'}, status=200)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
    
    @authorize_user
    def delete(self, request, comment_id): 
        comment = Comment.objects.get(
            id = comment_id
        )
        comment.delete()
        
        return JsonResponse({'message': 'DELETE_COMMNET'}, status=204)