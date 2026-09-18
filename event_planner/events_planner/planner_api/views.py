import jwt
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from events.models import Event
from django.contrib.auth import get_user_model, authenticate
from planner_api.serializers import EventSerializer
from planner_api.auth_utils import create_access_token, create_refresh_token


User = get_user_model()


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     user = self.request.user
    #     return Event.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        event = self.get_object()
        event.is_completed = True
        event.save(update_fields=['is_completed'])

        return Response(EventSerializer(event).data)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            username=request.data.get('cell_phone'),
            password=request.data.get('password'),
        )

        if not user:
            return Response({'error': 'Wrong credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'access': create_access_token(user),
            'refresh': create_refresh_token(user)
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            return Response({'error': '"refresh" is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired!!!'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token!'}, status=status.HTTP_401_UNAUTHORIZED)

        if payload.get('token_type') != 'refresh':
            return Response({'error': 'Wrong type'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'access': create_access_token(user)
        })
