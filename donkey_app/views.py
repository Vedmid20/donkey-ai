from .serializers import UserSerializer, ChatSerializer, MessageSerializer
from .models import User, Chat, Message
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import ollama


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


class OllamaResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def create(self, request, *args, **kwargs):
        prompt = request.data.get('prompt', '')

        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)
        chat, created = Chat.objects.get_or_create(owner=request.user)

        user_message = Message.objects.create(
            chat=chat,
            sender='User',
            content=prompt
        )

        client = ollama.Client()
        model = 'llama3'
        response = client.generate(model=model, prompt=prompt)

        ollama_message = Message.objects.create(
            chat=chat,
            sender='Ollama',
            content=response.response
        )

        return Response({"response": response.response})

    @action(detail=False, methods=['get'])
    def get_history(self, request):
        try:
            chat = Chat.objects.get(owner=request.user)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)
        messages = Message.objects.filter(chat=chat).order_by('timestamp')

        history = MessageSerializer(messages, many=True)

        return Response({"history": history.data})