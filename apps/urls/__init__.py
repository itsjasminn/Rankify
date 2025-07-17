
from apps.urls.student import urlpatterns as submission
from apps.urls.teachers import urlpatterns as teacher

urlpatterns=[
    *submission,
    *teacher
]
