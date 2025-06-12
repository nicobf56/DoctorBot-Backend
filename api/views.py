from sqlite3 import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status, generics
from api.core.response import generate_answer
from .serializers import ChatHistorySerializer, CorrectionSerializer, FeedbackSerializer
from .models import ChatHistory, Feedback
from api import serializers

class GenerateAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "No se proporcionó la pregunta."}, status=status.HTTP_400_BAD_REQUEST)

        answer, references = generate_answer(question)

        chat = ChatHistory.objects.create(
            user=request.user,
            question=question,
            answer=answer,
            references=references
        )

        return Response({
            "id": chat.id,
            "respuesta": answer,
            "referencias": references
        })


class ChatHistoryView(ListAPIView):
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatHistory.objects.filter(user=self.request.user).order_by('-created_at')


class ChatHistoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        chats = ChatHistory.objects.filter(user=user).order_by('-created_at')

        serialized = [
            {
                "id": chat.id,
                "pregunta": chat.question,
                "respuesta": chat.answer[:200] + "..." if len(chat.answer) > 200 else chat.answer,
                "fecha": chat.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for chat in chats
        ]

        return Response(serialized, status=status.HTTP_200_OK)
    

class ChatHistoryDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            chat = ChatHistory.objects.get(pk=pk, user=request.user)
        except ChatHistory.DoesNotExist:
            return Response({"error": "Chat no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "pregunta": chat.question,
            "respuesta": chat.answer,
            "referencias": chat.references
        })

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hola, {request.user.username}! Estás autenticado correctamente."
        })


class CorrectionCreateView(generics.CreateAPIView):
    serializer_class = CorrectionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        Feedback.objects.update_or_create(
        user=self.request.user,
        chat=serializer.validated_data["chat"],
        defaults={"vote": serializer.validated_data["vote"]},
    )
        
class UserFeedbackListView(ListAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)
