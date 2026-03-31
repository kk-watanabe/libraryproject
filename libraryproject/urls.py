from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('libraryapp.urls')),
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

