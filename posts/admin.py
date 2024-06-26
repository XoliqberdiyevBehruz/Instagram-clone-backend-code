from django.contrib import admin
from .models import Post, PostComment, PostLike, CommentLike

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'caption', 'created_time')
    search_fields = ('id', 'author')

class PostCommentAdmin(admin.ModelAdmin):
    ist_display = ('id', 'author', 'post', 'created_time')
    search_fields = ('id', 'author')

class PostLikeAdmin(admin.ModelAdmin):
    ist_display = ('id', 'author', 'post', 'created_time')
    search_fields = ('id', 'author')

class CommentLikeAdmin(admin.ModelAdmin):
    ist_display = ('id', 'author', 'comment', 'created_time')
    search_fields = ('id', 'author')

admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)