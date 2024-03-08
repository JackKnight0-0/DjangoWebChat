from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views import generic as django_generic
from rest_framework import generics as drf_generic
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.db.models import Q

from .serializers import UserSerializer, MessageSerializer

from accounts.models import CustomUser
from .models import ChatOnoToOne, Message
from .permissions import EmailIsVerified


class ChatLobby(LoginRequiredMixin, EmailIsVerified, django_generic.TemplateView):
    """
    View for render user chats
    """
    template_name = 'chats.html'

    def get_new_chat_friends(self):
        chats = ChatOnoToOne.objects.filter(users__in=[self.request.user, ])
        return self.request.user.friend.filter(~Q(chats__in=chats))

    def get_context_data(self, **kwargs):
        context = super(ChatLobby, self).get_context_data(**kwargs)
        context['chats'] = self.request.user.chats
        context['friends'] = self.get_new_chat_friends()
        return context


class CreateNewChat(LoginRequiredMixin, EmailIsVerified, django_generic.FormView):
    """
    Creates a new chat for the user and his friend, and checks if this chat does not exist already
    """

    def get_with_user(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs.get('user_pk'))

    def create_users_for_chat(self, chat):
        with_user = self.get_with_user()
        self.check_if_chat_not_exists(with_user=with_user)
        chat.users.add(with_user)  # create chat with a friend user object
        chat.users.add(self.request.user)  # create for current user chat
        chat.save()

    def check_if_chat_not_exists(self, with_user):
        if ChatOnoToOne.objects.filter(users=with_user).filter(users=self.request.user).exists():
            raise Http404

    def create_chat(self):
        chat = ChatOnoToOne.objects.create()
        self.create_users_for_chat(chat=chat)
        return chat

    def post(self, request, *args, **kwargs):
        chat = self.create_chat()
        return redirect(chat.get_absolute_url())


class ChatOneToOneView(LoginRequiredMixin, EmailIsVerified, UserPassesTestMixin, django_generic.DetailView):
    """
    Rendering messages and users for chat, checking if user having access to this chat
    """
    model = ChatOnoToOne
    context_object_name = 'chat'
    template_name = 'chat/one_to_one_chat.html'

    def get_object(self, queryset=None):
        return get_object_or_404(ChatOnoToOne, uuid=self.kwargs.get('uuid'))

    def get_user_friend(self):
        chat = self.get_object()
        return chat.users.all().exclude(id=self.request.user.id)[0]

    def update_new_message(self, messages):
        for message in messages:
            message.is_read = True
            message.save()

    def get_context_data(self, **kwargs):
        """
        This function is optimizing a message query by rendering only last 50
        """
        context = super(ChatOneToOneView, self).get_context_data(**kwargs)
        limit = 50
        new_messages = Message.objects.filter(Q(chat=self.get_object()) & Q(is_read=False)).exclude(
            from_user=self.request.user).order_by('create_at')[:50]
        if len(new_messages) >= 50:
            limit = 10
        old_messages = Message.objects.filter(
            Q(chat=self.get_object()) & (
                    Q(is_read=True) | Q(from_user=self.request.user)))[:limit:-1]
        context['new_messages'] = new_messages[:]  # creating a copy of a query, so we can change they're fields
        context['old_messages'] = list(old_messages)
        context['friend'] = self.get_user_friend()
        self.update_new_message(new_messages)
        return context

    def test_func(self):
        if self.get_object().users.filter(id=self.request.user.id).exists():
            return True
        return False


class GetMessagesAPIView(LoginRequiredMixin, EmailIsVerified, drf_generic.GenericAPIView):
    """
    Checking if user having access to chat and messages, and if so return JSON messages for current chat
    """

    def get_chat(self):
        chat = get_object_or_404(ChatOnoToOne, uuid=self.kwargs.get('uuid'))
        if chat.users.filter(id=self.request.user.id).exists():
            return chat
        raise Http404

    def get_message_before(self, chat, message):
        """
        Query 50 old messages from top before an old message
        """
        limit = 50
        messages = MessageSerializer(data=chat.messages.filter(pk__lt=message.pk)[:limit], many=True,
                                     context={'user': self.request.user})
        messages.is_valid()
        return messages

    def get_message_after(self, chat, message):
        """
        Query 50 for a new message from bottom chat box
        """
        limit = 50
        messages = MessageSerializer(data=chat.messages.filter(pk__gt=message.pk)[:limit:-1], many=True,
                                     context={'user': self.request.user})
        messages.is_valid()
        return messages

    def get_messages(self):
        chat = self.get_chat()
        if self.request.GET.get('before', False):
            message = get_object_or_404(Message, pk=self.request.GET.get('before', None))
            return self.get_message_before(chat=chat, message=message)
        else:
            message = get_object_or_404(Message, pk=self.request.GET.get('after', None))
            return self.get_message_after(chat=chat, message=message)

    def get(self, request, *args, **kwargs):
        messages = self.get_messages()
        return JsonResponse({'messages': messages.data})


# friends

class FindFriendsAPI(EmailIsVerified, LoginRequiredMixin, drf_generic.GenericAPIView):
    """
    Returns JSON users data that match the search pattern and not friend with current user
    """

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        friends_pk = [pk['pk'] - 1 for pk in self.request.user.friend.values('pk')]
        users = CustomUser.objects.all().filter(
            Q(username__istartswith=query) | Q(username__regex=f'\b{query}\b')).filter(
            ~Q(friend__in=friends_pk)).exclude(pk=self.request.user.pk)
        return JsonResponse({'data': UserSerializer(users, many=True).data})


class FindFriends(EmailIsVerified, LoginRequiredMixin, django_generic.ListView):
    """
    Rendering friend users in template
    """
    model = get_user_model()
    template_name = 'chat/friend_find.html'
    context_object_name = 'new_friends'

    def get_queryset(self):
        friends_pk = [pk['pk'] for pk in self.request.user.friend.values('pk')]
        return get_user_model().objects.filter(~Q(friend__in=friends_pk)).exclude(pk=self.request.user.pk)

    def get_context_data(self, *args, **kwargs):
        context = super(FindFriends, self).get_context_data(*args, **kwargs)
        context['my_friends'] = self.request.user.friend.all()
        return context


class AddNewFriend(LoginRequiredMixin, django_generic.FormView):
    """
    Add a new friend to user and checking if user not having such a friend already
    """

    def get_friend(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs.get('friend_pk'))

    def check_if_already_friend(self):
        if self.request.user.friend.filter(pk=self.get_friend().pk).exists():
            raise Http404

    def add_friend_to_user(self):
        self.check_if_already_friend()
        self.request.user.friend.add(self.get_friend())
        self.request.user.save()

    def get_success_url(self):
        friend = self.get_friend()
        return redirect(reverse('profile_detail', kwargs={'username': friend.username}))

    def post(self, request, *args, **kwargs):
        self.add_friend_to_user()
        return self.get_success_url()


class DeleteFriendView(LoginRequiredMixin, EmailIsVerified, django_generic.View):

    def get_success_url(self):
        friend = self.get_friend()
        return redirect(reverse('profile_detail', kwargs={'username': friend.username}))

    def get_friend(self):
        return get_object_or_404(get_user_model(), username=self.kwargs.get('username', None))

    def check_if_user_friends(self):
        friend = self.get_friend()
        if friend not in self.request.user.friend.all():
            raise Http404
        return friend

    def delete_chats(self):
        chat = ChatOnoToOne.objects.filter(users__in=[self.request.user, ]).filter(users__in=[self.get_friend(), ])
        if chat.exists():
            chat.delete()

    def delete_friend(self):
        friend = self.check_if_user_friends()
        self.delete_chats()
        self.request.user.friend.remove(friend)

    def post(self, request, *args, **kwargs):
        self.delete_friend()
        return self.get_success_url()


# start page

class StartPageView(UserPassesTestMixin, django_generic.TemplateView):
    """
    Rendering start page for new users, only logout or anonymous users having access
    """
    template_name = 'start_page.html'

    def test_func(self):
        if self.request.user.is_authenticated:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)
