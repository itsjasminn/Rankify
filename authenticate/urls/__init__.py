from authenticate.urls.auth import urlpatterns as auth
from authenticate.urls.group import urlpatterns as groups

urlpatterns = [
    *auth,
    *groups
]
