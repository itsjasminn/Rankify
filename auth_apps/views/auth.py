from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth_apps.models import User, Sessions
from auth_apps.serializer import SessionModelSerializer


from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['auth'])
class CustomerTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        original_response = super().post(request, *args, **kwargs)
        if original_response.status_code == 200 and 'access' in original_response.data:
            phone = request.data.get('phone')
            user = User.objects.filter(phone=phone).first()
            device = {
                'device_name': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'ip_address': request.META.get('REMOTE_ADDR', '127.0.0.1'),
            }
            query = Sessions.objects.filter(device_name=device['device_name'])
            sessions = Sessions.objects.filter(user=user)
            if not query.exists():
                if sessions.count() >= 3:
                    serializer = SessionModelSerializer(instance=sessions, many=True)
                    return Response(data=serializer.data, status=HTTP_200_OK)
                else:
                    Sessions.objects.create(user=user, **device)
            user.last_login = now()
            user.save(update_fields=["last_login"])
        return original_response



@extend_schema(tags=['auth'])
class CustomerTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=['auth'])
class SessionDestroyAPIView(DestroyAPIView):
    queryset = Sessions.objects.all()
    serializer_class = SessionModelSerializer
    lookup_field = 'pk'
