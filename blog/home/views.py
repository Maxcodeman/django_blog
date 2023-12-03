from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views import View

from home.models import ArticleCategory, Article, Comment


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

class DetailView(View):
    def get(self,request):
        #获取文档id
        id=request.GET.get('id')

        #获取博客分类信息
        categories=ArticleCategory.objects.all()

        try:
            article=Article.objects.get(id=id)
        except Article.DoesNotExist:
            return render(request,'404.html')
        else:
            article.total_views+=1
            article.save()

        #获取热点数据
        hot_articles=Article.objects.order_by('-total_views')[:9]

        # 获取分页参数
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 10)

        # 获取当前文章的评论数据
        comments = Comment.objects.filter(article=article).order_by('-created')
        #获取评论总数
        total_count=comments.count()

        # 创建分页器
        paginator = Paginator(comments, page_size)

        # 进行分页处理
        try:
            page_comments = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')

        # 总页数
        total_pages = paginator.num_pages

        context={
            "categories":categories,
            "category":article.category,
            "article":article,
            "comments":page_comments,
            'hot_articles':hot_articles,
            'page_num':page_num,
            'page_size':page_size,
            'total_count':total_count,
            'total_pages':total_pages,
        }

        return render(request,"detail.html",context=context)

    def post(self,request):
        #获取用户信息
        user=request.user

        #判断用户是否登录
        if user and user.is_authenticated:
            #接收参数
            id=request.POST.get("id")
            content=request.POST.get("content")

            #判断文章是否存在
            try:
                article=Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此文章')

            #保存到数据
            Comment.objects.create(
                content=content,
                article=article,
                user=user
            )

            #修改文章评论数量
            article.comments_count+=1
            article.save()

            #拼接跳转路由
            from django.urls import reverse
            path=reverse('home:detail')+'?id={}'.format(article.id)
            return redirect(path)

        else:
            #没有登录则跳转到登录页面
            from django.urls import reverse
            return redirect(reverse('users:login'))