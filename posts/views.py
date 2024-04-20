from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from shared.custom_pagination import CustomPagination
from .models import Post, PostComment, PostLike, CommentLike
from .serializers import PostLikeSerializer, CommentSerializer, CommentLikeSerializer, PostSerializer
from rest_framework.views import APIView


class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success':True,
            'status':status.HTTP_200_OK,
            'message':'Post successfully updated',
            'data':serializer.data
        })
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response({
            'success':True,
            "status":status.HTTP_204_NO_CONTENT,
            'message':"Post successfully deleted"
        })
    

class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset

class PostCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)

class CommentListCreateApiView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    pagination_class = CustomPagination
    queryset = PostComment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostLike.objects.filter(post_id=post_id)
        return queryset
    
class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        queryset = CommentLike.objects.filter(comment_id=comment_id)
        return queryset
    

class CommentLikeCreateView(generics.CreateAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    
class PostLikeView(APIView):

    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(author=self.request.user, post_id=pk)
            post_like.delete()
            data = {
                "succes":True,
                "message":"UnLiked",
                'data': None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)
        
        except PostLike.DoesNotExist:
            post_like = PostLike.objects.create(author=self.request.user, post_id=pk)
            serializer = PostLikeSerializer(post_like)
            data = {
                "success":True, 
                "message":"Liked",
                "data":serializer.data
            }

            return Response(data, status=status.HTTP_201_CREATED)
        

class CommentLikeView(APIView):
    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(author=self.request.user, comment_id=pk)
            comment_like.delete()
            data = {
                'success':True,
                "message":"Unliked",
                "data":None
            }
            return Response(data, status=status.HTTP_204_NO_CONTENT)

        except CommentLike.DoesNotExist:
            comment_like = CommentLike.objects.create(author=self.request.user, comment_id=pk)
            serialezer = CommentLikeSerializer(comment_like)
            data={
                "success":True,
                "message":"Liked",
                "data":serialezer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
        