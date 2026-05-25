import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import User
from .permissions import IsAdmin
from .serializers import (
    CurrentUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """Register a new user and return an auth token.

    Accepts username, email, password, password confirmation, and role (student/teacher).
    Immediately creates a token so the user is authenticated right after registration.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        logger.info(f"New user registered: {user.username} (role: {user.role})")
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a user and return an auth token.

    Validates username and password, then returns the user object and a token.
    Uses get_or_create so repeated logins reuse the same token (no token proliferation).
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"User logged in: {user.username}")
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
        })


class LogoutView(APIView):
    """Log out the current user by deleting their auth token server-side.

    Destroying the token prevents token reuse after logout. Subsequent requests
    with that token will be rejected as unauthorized, even if the token is still
    present on the client. This is a real security boundary, not just a UI feature.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        request.user.auth_token.delete()
        logger.info(f"User logged out: {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Return or update the currently authenticated user's profile.

    Uses CurrentUserSerializer on writes to prevent self-escalation: role,
    username, and email are read-only here. Admin user management endpoints
    use the unrestricted UserSerializer.
    """

    serializer_class = CurrentUserSerializer

    def get_object(self) -> User:
        return self.request.user


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""

    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user (admin only)."""

    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    queryset = User.objects.all()
