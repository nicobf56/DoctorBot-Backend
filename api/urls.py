from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import GenerateAnswerAPIView, ProtectedAPIView, ChatHistoryListView, ChatHistoryDetailView, CorrectionCreateView, FeedbackCreateView, UserFeedbackListView

urlpatterns = [
    path('generar-respuesta/', GenerateAnswerAPIView.as_view(), name='generate_answer'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protegido/', ProtectedAPIView.as_view(), name='protected'),
    path("historial/", ChatHistoryListView.as_view(), name="historial-list"),
    path("historial/<int:pk>/", ChatHistoryDetailView.as_view(), name="historial-detail"),
    path('corrections/', CorrectionCreateView.as_view(), name='add-correction'),
    path('feedback/', FeedbackCreateView.as_view(), name='submit-feedback'),
    path('feedback/user/', UserFeedbackListView.as_view(), name='user-feedback')
]
