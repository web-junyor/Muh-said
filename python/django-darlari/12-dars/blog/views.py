from django.http import Http404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post

class BlogListView(ListView):
    model = Post
    template_name = 'home.html'

    def get_queryset(self):
        user = self.request.user
        qs = Post.objects.order_by('-created_at')

        if user.is_staff:
            return qs

        if user.is_authenticated:
            return qs.filter(author=user)

        # login bo‘lmaganlar ro‘yxat ko‘rmaydi
        return Post.objects.none()


class BlogDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        user = self.request.user

        # admin/staff hammasini ko‘radi
        if user.is_staff:
            return post

        # author o‘z postini ko‘radi
        if user.is_authenticated and post.author_id == user.id:
            return post

        # telegram user: faqat token bilan
        token = self.request.GET.get("t")
        if token and str(post.access_token) == token:
            return post

        raise Http404("Not found")


class BlogCreateView(CreateView):
    model = Post
    template_name = 'post_new.html'
    fields = ['title', 'body', 'image']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogUpdateView(UpdateView):
    model = Post
    template_name = 'post_edit.html'
    fields = ['title', 'body', 'image']

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        token = self.request.GET.get('t')
        if pk and token:
            try:
                post = Post.objects.get(pk=pk)
                if str(post.access_token) == token:
                    return post
            except Post.DoesNotExist:
                pass
        return super().get_object(queryset)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Post.objects.all()
        if user.is_authenticated:
            return Post.objects.filter(author=user)
        return Post.objects.none()


class BlogDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        token = self.request.GET.get('t')
        if pk and token:
            try:
                post = Post.objects.get(pk=pk)
                if str(post.access_token) == token:
                    return post
            except Post.DoesNotExist:
                pass
        return super().get_object(queryset)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Post.objects.all()
        if user.is_authenticated:
            return Post.objects.filter(author=user)
        return Post.objects.none()
