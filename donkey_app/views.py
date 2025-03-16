from .serializers import UserSerializer, ChatSerializer, MessageSerializer
from .models import User, Chat, Message
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
import ollama


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def get_queryset(self):
        user = self.request.user
        chat_id = self.request.query_params.get('chat_id')
        if chat_id:
            try:
                chat = Chat.objects.get(chat_id=chat_id)
                if chat.owner != user:
                    raise PermissionDenied("You do not have access to this chat.")
                return Chat.objects.filter(chat_id=chat_id)
            except Chat.DoesNotExist:
                raise PermissionDenied("Chat not found.")
        else:
            return Chat.objects.filter(owner=user)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class MessagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OllamaResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    http_method_names = ['post', 'get']

    def create(self, request, *args, **kwargs):
        print("CREATE METHOD CALLED")
        prompt = request.data.get('prompt', '')
        chat_id = request.query_params.get('chat_id')
        if not prompt:
            return Response({"error": "Prompt is required"}, status=400)

        if not chat_id:
            chat, created = Chat.objects.get_or_create(owner=request.user)
        else:
            chats = Chat.objects.filter(chat_id=chat_id, owner=request.user)
            if chats.count() == 0:
                return Response({"error": "Chat not found"}, status=404)
            elif chats.count() > 1:
                return Response({"error": "Multiple chats found with the same chat_id, please clarify the chat_id"}, status=400)
            else:
                chat = chats.first()

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
        chat_id = request.query_params.get('chat_id')

        if not chat_id:
            return Response({"error": "chat_id is required"}, status=400)
        chats = Chat.objects.filter(chat_id=chat_id, owner=request.user)

        if chats.count() == 0:
            return Response({"error": "Chat not found"}, status=404)
        elif chats.count() > 1:
            return Response({"error": "Multiple chats found with the same chat_id, please clarify the chat_id"}, status=400)
        else:
            chat = chats.first()
        messages = Message.objects.filter(chat=chat).order_by('timestamp')
        history = MessageSerializer(messages, many=True)

        return Response({"history": history.data})



