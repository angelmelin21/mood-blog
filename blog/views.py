from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog, Reaction, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone
import re


# HOME PAGE
def home(request):
    mood = request.GET.get('mood')

    # Only show published blogs (is_draft=False), order by newest first
    if mood:
        blogs = Blog.objects.filter(mood=mood, is_draft=False).order_by('-created_at')
    else:
        blogs = Blog.objects.filter(is_draft=False).order_by('-created_at')

    # Count reactions
    for blog in blogs:
        blog.thumbs_up = Reaction.objects.filter(blog=blog, type='like').count()
        blog.thumbs_down = Reaction.objects.filter(blog=blog, type='dislike').count()
        blog.heart = Reaction.objects.filter(blog=blog, type='heart').count()

    return render(request, 'home.html', {'blogs': blogs})


# CREATE BLOG (FIXED - SINGLE VERSION)
@login_required
def create_blog(request):
    draft = None
    draft_id = request.GET.get('draft')
    
    # If there's a draft ID in the URL, load that draft
    if draft_id:
        try:
            draft = Blog.objects.get(id=draft_id, author=request.user, is_draft=True)
        except Blog.DoesNotExist:
            draft = None
    
    if request.method == "POST":
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        mood = request.POST.get('mood', 'Happy')
        anonymous = request.POST.get('anonymous') == 'on'
        draft_id = request.POST.get('draft_id')
        action = request.POST.get('action')

        cover_image = request.FILES.get('cover_image')
        spotify_link = request.POST.get('spotify_link')
        audio_file = request.FILES.get('audio_file')

        # Calculate reading time
        word_count = len(content.split())
        reading_time = max(1, round(word_count / 200))

        if draft_id and draft_id != '':
            # Update existing draft
            blog = get_object_or_404(Blog, id=draft_id, author=request.user, is_draft=True)
            blog.title = title
            blog.content = content
            blog.mood = mood
            blog.anonymous = anonymous
            blog.reading_time = reading_time
            if cover_image:
                blog.cover_image = cover_image
            if spotify_link:
                blog.spotify_link = spotify_link
            if audio_file:
                blog.audio_file = audio_file
            
            if action == 'publish':
                blog.is_draft = False  # PUBLISH
            else:
                blog.is_draft = True  # Keep as draft
            blog.save()
        else:
            # Create new blog
            blog = Blog.objects.create(
                title=title,
                content=content,
                mood=mood,
                author=request.user,
                anonymous=anonymous,
                cover_image=cover_image,
                spotify_link=spotify_link,
                audio_file=audio_file,
                reading_time=reading_time,
                is_draft=(action != 'publish')
            )

        return redirect('/')

    return render(request, 'create_blog.html', {'draft': draft})


# LOGIN VIEW
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


# LOGOUT VIEW
def logout_view(request):
    logout(request)
    return redirect('/')


# SIGNUP
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


# SAVED BLOGS
@login_required
def saved_blogs(request):
    saved_ids = request.session.get("saved_blogs", [])
    blogs = Blog.objects.filter(id__in=saved_ids)
    
    for blog in blogs:
        blog.thumbs_up = Reaction.objects.filter(blog=blog, type='like').count()
        blog.thumbs_down = Reaction.objects.filter(blog=blog, type='dislike').count()
        blog.heart = Reaction.objects.filter(blog=blog, type='heart').count()
    
    return render(request, 'saved.html', {'blogs': blogs})


# REACT TO BLOG
def react(request, blog_id, reaction):
    blog = get_object_or_404(Blog, id=blog_id)

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    existing = Reaction.objects.filter(
        blog=blog,
        session_key=session_key
    ).first()

    if existing:
        if existing.type == reaction:
            existing.delete()
        else:
            existing.type = reaction
            existing.save()
    else:
        Reaction.objects.create(
            blog=blog,
            type=reaction,
            session_key=session_key
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))


# COMMENT
def comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        text = request.POST.get("text")
        Comment.objects.create(
            blog=blog,
            text=text
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))


# SAVE BLOG
def save_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    saved = request.session.get("saved_blogs", [])

    if blog_id not in saved:
        saved.append(blog_id)

    request.session["saved_blogs"] = saved
    return redirect(request.META.get('HTTP_REFERER', '/'))


# UNSAVE BLOG
@login_required
def unsave_blog(request, blog_id):
    saved = request.session.get("saved_blogs", [])
    
    if blog_id in saved:
        saved.remove(blog_id)
    
    request.session["saved_blogs"] = saved
    return redirect('saved')


# SAVE DRAFT (FIXED)
@login_required
def save_draft(request):
    if request.method == "POST":
        try:
            title = request.POST.get('title', '')
            content = request.POST.get('content', '')
            mood = request.POST.get('mood', 'Happy')
            anonymous = request.POST.get('anonymous') == 'on'
            draft_id = request.POST.get('draft_id')
            
            print(f"Saving draft - Title: {title}, ID: {draft_id}")
            
            if draft_id and draft_id != '':
                # Update existing draft
                draft = get_object_or_404(Blog, id=draft_id, author=request.user, is_draft=True)
                draft.title = title
                draft.content = content
                draft.mood = mood
                draft.anonymous = anonymous
                draft.save()
                message = 'Draft updated'
            else:
                # Create new draft
                draft = Blog.objects.create(
                    title=title,
                    content=content,
                    mood=mood,
                    author=request.user,
                    anonymous=anonymous,
                    is_draft=True
                )
                message = 'Draft created'
            
            return JsonResponse({
                'status': 'success',
                'draft_id': draft.id,
                'message': message,
                'saved_at': timezone.now().strftime('%I:%M %p')
            })
        except Exception as e:
            print(f"Error saving draft: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# PUBLISH DRAFT
@login_required
def publish_draft(request, draft_id):
    draft = get_object_or_404(Blog, id=draft_id, author=request.user, is_draft=True)
    
    if request.method == "POST":
        draft.title = request.POST.get('title', draft.title)
        draft.content = request.POST.get('content', draft.content)
        draft.mood = request.POST.get('mood', draft.mood)
        draft.anonymous = request.POST.get('anonymous') == 'on'
        draft.cover_image = request.FILES.get('cover_image') or draft.cover_image
        draft.spotify_link = request.POST.get('spotify_link') or draft.spotify_link
        draft.audio_file = request.FILES.get('audio_file') or draft.audio_file
        
        word_count = len(draft.content.split())
        draft.reading_time = max(1, round(word_count / 200))
        
        draft.is_draft = False
        draft.save()
        
        return redirect('home')
    
    return redirect(f'/create/?draft={draft_id}')


# MY DRAFTS PAGE
@login_required
def my_drafts(request):
    drafts = Blog.objects.filter(author=request.user, is_draft=True).order_by('-last_saved')
    return render(request, 'drafts.html', {'drafts': drafts})


# DELETE DRAFT
@login_required
def delete_draft(request, draft_id):
    if request.method == "POST":
        try:
            draft = get_object_or_404(Blog, id=draft_id, author=request.user, is_draft=True)
            draft.delete()
            return JsonResponse({'status': 'success', 'message': 'Draft deleted successfully'})
        except Blog.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Draft not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# LOAD DRAFT
@login_required
def load_draft(request, draft_id):
    draft = get_object_or_404(Blog, id=draft_id, author=request.user, is_draft=True)
    return render(request, 'create_blog.html', {'draft': draft})


# EXPORT BLOG AS PDF
def export_pdf(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{blog.title}.pdf"'
    
    template_path = 'blog_pdf.html'
    context = {'blog': blog}
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('PDF generation error', status=400)
    
    return response


# GET BLOG JSON (for AJAX)
def get_blog_json(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, is_draft=False)
    return JsonResponse({
        'success': True,
        'title': blog.title,
        'content': blog.content,
        'mood': blog.mood,
        'author': str(blog.author) if not blog.anonymous else 'Anonymous',
        'thumbs_up': Reaction.objects.filter(blog=blog, type='like').count(),
        'thumbs_down': Reaction.objects.filter(blog=blog, type='dislike').count(),
        'heart': Reaction.objects.filter(blog=blog, type='heart').count(),
    })


# CLEAN HTML CONTENT
def clean_html_content(content):
    content = re.sub(r'class="[^"]*"', '', content)
    content = re.sub(r'style="[^"]*"', '', content)
    content = re.sub(r'<o:p>|</o:p>', '', content)
    content = re.sub(r'<!--\[if gte mso 9\]>.*?<!\[endif\]-->', '', content, flags=re.DOTALL)
    content = re.sub(r'<meta[^>]*>', '', content)
    content = re.sub(r'<xml[^>]*>.*?</xml>', '', content, flags=re.DOTALL)
    content = re.sub(r'<!--StartFragment-->|<!--EndFragment-->', '', content)
    return content


# DELETE BLOG (only for author)
@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    
    if request.user == blog.author:
        blog.delete()
        return redirect('home')
    else:
        return HttpResponse('You are not authorized to delete this blog', status=403)