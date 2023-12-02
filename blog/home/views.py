from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View

from home.models import ArticleCategory, Article


# Create your views here.
class IndexView(View):
    """首页广告"""
    def get(self,request):
        """
        提供首页广告界面
        """
        #1.获取所有分类信息
        categories=ArticleCategory.objects.all()
        #2.接收用户点击的分类id,默认值为1
        cat_id=request.GET.get('cat_id',1)
        #3.根据分类id进行分类的查询
        try:
            category=ArticleCategory.objects.get(id=cat_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseNotFound('没有此分类')


        #4.获取分页参数
        page_num=request.GET.get('page_num',1)
        page_size=request.GET.get('page_size',10)
        #5.根据分类信息查询文章数据
        articles=Article.objects.filter(category=category)
        #6.创建分页器
        paginator=Paginator(articles,page_size)
        #7.进行分页处理
        try:
            page_articles=paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 总页数
        total_pages=paginator.num_pages
        #8.组织数据传递给模版
        context = {
            'categories': categories,
            'category': category,
            'articles':page_articles,
            'page_num':page_num,
            'page_size':page_size,
            'total_pages':total_pages
        }

        return render(request,"index.html",context=context)

