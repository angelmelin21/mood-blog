from django.contrib import admin
from django.urls import path, include
from blog import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('create/', views.create_blog, name='create'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('saved/', views.saved_blogs, name='saved'),
    path('react/<int:blog_id>/<str:reaction>/', views.react, name='react'),
    path('comment/<int:blog_id>/', views.comment, name='comment'),
    path('save/<int:blog_id>/', views.save_blog, name='save_blog'),
    path('unsave/<int:blog_id>/', views.unsave_blog, name='unsave_blog'),  # ADD THIS LINE
    path('save-draft/', views.save_draft, name='save_draft'),
    path('publish-draft/<int:draft_id>/', views.publish_draft, name='publish_draft'),
    path('my-drafts/', views.my_drafts, name='my_drafts'),
    path('delete-draft/<int:draft_id>/', views.delete_draft, name='delete_draft'),
    path('export-pdf/<int:blog_id>/', views.export_pdf, name='export_pdf'),
    path('get-blog/<int:blog_id>/', views.get_blog_json, name='get_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)