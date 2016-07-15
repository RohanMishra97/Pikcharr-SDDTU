from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import AlbumForm, PicForm, UserForm
from .models import Album, Pic


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def create_album(request):
    if not request.user.is_authenticated():
        return render(request, 'image/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_cover = request.FILES['album_cover']
            file_type = album.album_cover.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'image/create_album.html', context)
            album.save()
            return render(request, 'image/detail.html', {'album': album})
        context = {  "form": form,       }
        return render(request, 'image/create_album.html', context)


def create_pic(request, album_id):
    form = PicForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        albums_pics = album.pic_set.all()
        for s in albums_pics:
            if s.pic_title == form.cleaned_data.get("pic_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that pic',
                }
                return render(request, 'image/create_pic.html', context)
        pic = form.save(commit=False)
        pic.album = album
        pic.pic_file = request.FILES['pic_file']
        file_type = pic.pic_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in IMAGE_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Image file must be PNG, JPG, or JPEG',
            }
            return render(request, 'image/create_pic.html', context)

        pic.save()
        return render(request, 'image/detail.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'image/create_pic.html', context)


def delete_album(request, album_id):
    album = Album.objects.get(pk=album_id)
    album.delete()
    albums = Album.objects.filter(user=request.user)
    return render(request, 'image/index.html', {'albums': albums})


def delete_pic(request, album_id, pic_id):
    album = get_object_or_404(Album, pk=album_id)
    pic = Pic.objects.get(pk=pic_id)
    pic.delete()
    return render(request, 'image/detail.html', {'album': album})


def detail(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'image/login.html')
    else:
        user = request.user
        album = get_object_or_404(Album, pk=album_id)
        return render(request, 'image/detail.html', {'album': album, 'user': user})


def favorite(request, pic_id):
    pic = get_object_or_404(Pic, pk=pic_id)
    try:
        if pic.is_favorite:
            pic.is_favorite = False
        else:
            pic.is_favorite = True
        pic.save()
    except (KeyError, Pic.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except (KeyError, Album.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'image/login.html')
    else:
        albums = Album.objects.filter(user=request.user)
        pic_results = Pic.objects.all()
        query = request.GET.get("q")
        if query:
            albums = albums.filter(
                Q(album_title__icontains=query)
            ).distinct()
            pic_results = pic_results.filter(
                Q(pic_title__icontains=query)
            ).distinct()
            return render(request, 'image/index.html', {
                'albums': albums,
                'pics': pic_results,
            })
        else:
            return render(request, 'image/index.html', {'albums': albums})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'image/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'image/index.html', {'albums': albums})
            else:
                return render(request, 'image/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'image/login.html', {'error_message': 'Invalid login'})
    return render(request, 'image/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'image/index.html', {'albums': albums})
    context = {
        "form": form,
    }
    return render(request, 'image/register.html', context)


def pics(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'image/login.html')
    else:
        try:
            pic_ids = []
            for album in Album.objects.filter(user=request.user):
                for pic in album.pic_set.all():
                    pic_ids.append(pic.pk)
            users_pics = Pic.objects.filter(pk__in=pic_ids)
            if filter_by == 'favorites':
                users_pics = users_pics.filter(is_favorite=True)
        except Album.DoesNotExist:
            users_pics = []
        return render(request, 'image/pics.html', {
            'pic_list': users_pics,
            'filter_by': filter_by,
        })
