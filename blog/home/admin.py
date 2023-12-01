from django.contrib import admin
from home.models import ArticleCategory, Article

#注册模型
admin.site.register(ArticleCategory)

admin.site.register(Article)
