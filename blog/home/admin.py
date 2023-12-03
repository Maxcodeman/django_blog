from django.contrib import admin
from home.models import ArticleCategory, Article, Comment

#注册模型
admin.site.register(ArticleCategory)

admin.site.register(Article)

admin.site.register(Comment)
