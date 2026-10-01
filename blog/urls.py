from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_blog, name='create'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('saved/', views.saved_blogs, name='saved'),
    path('react/<int:blog_id>/<str:reaction>/', views.react, name='react'),
    path('comment/<int:blog_id>/', views.comment, name='comment'),
    path('save/<int:blog_id>/', views.save_blog, name='save_blog'),
    path('unsave/<int:blog_id>/', views.unsave_blog, name='unsave_blog'),
    
    # DRAFT URLs - MAKE SURE THESE ARE ALL HERE
    path('save-draft/', views.save_draft, name='save_draft'),
    path('publish-draft/<int:draft_id>/', views.publish_draft, name='publish_draft'),
    path('my-drafts/', views.my_drafts, name='my_drafts'),
    path('delete-draft/<int:draft_id>/', views.delete_draft, name='delete_draft'),
    path('load-draft/<int:draft_id>/', views.load_draft, name='load_draft'),
    
    # PDF EXPORT
    path('export-pdf/<int:blog_id>/', views.export_pdf, name='export_pdf'),

    path('get-blog/<int:blog_id>/', views.get_blog_json, name='get_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
]