from django.urls import path
from auth_apps.views import CustomerTokenObtainPairView, CustomerTokenRefreshView, SessionDestroyAPIView

urlpatterns=[
    path('login/', CustomerTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('sessison/delete<int:pk>/', SessionDestroyAPIView.as_view(), name='session-delete'),
    path('token/refresh/', CustomerTokenRefreshView.as_view(), name='token_refresh'),
]