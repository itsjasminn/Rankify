from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from auth_apps.models import User, Group, Sessions


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'full_name', 'phone', 'group', 'date_joined', 'last_login', 'role')
        read_only_fields = ('id', 'date_joined', 'last_login')


class GroupUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('group',)


class GroupModelSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('name', 'teacher', 'course')
        read_only_fields = ('id',)


class TeacherUserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()


class SessionModelSerializer(ModelSerializer):
    class Meta:
        model = Sessions
        fields = ('id', 'device_name', 'ip_address', 'user')
