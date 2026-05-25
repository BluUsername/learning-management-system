from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def api_root(request):
    return JsonResponse({
        'status': 'online',
        'application': 'LearnHub LMS API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'courses': '/api/courses/',
            'enrollments': '/api/enrollments/',
            'assignments': '/api/courses/<id>/assignments/',
            'submissions': '/api/assignments/<id>/submissions/',
            'achievements': '/api/achievements/',
            'chat': '/api/chat/conversations/',
            'users': '/api/users/',
            'admin': '/admin/',
            'docs': '/api/docs/',
            'redoc': '/api/redoc/',
        },
        'frontend': 'https://thelearnhub.netlify.app',
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('achievements.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Serve uploaded media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
