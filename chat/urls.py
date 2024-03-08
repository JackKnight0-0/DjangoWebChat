from django.urls import path

from .views import ChatLobby, ChatOneToOneView, CreateNewChat, FindFriends, AddNewFriend, FindFriendsAPI, StartPageView, \
    GetMessagesAPIView, DeleteFriendView

urlpatterns = [
    # start page
    path('', StartPageView.as_view(), name='start_page'),
    # chats
    path('chats/', ChatLobby.as_view(), name='home'),
    path('chat/<uuid:uuid>/', ChatOneToOneView.as_view(), name='chat_detail'),
    path('api/v1/chat/<uuid:uuid>/', GetMessagesAPIView.as_view()),
    path('create/chat/<int:user_pk>/', CreateNewChat.as_view(), name='new_chat'),
    # search and friend
    path('friends/api/search/', FindFriendsAPI.as_view()),
    path('friends/', FindFriends.as_view(), name='find_friends'),
    path('friend/delete/<slug:username>/', DeleteFriendView.as_view(), name='delete_friend'),
    path('new/friend/<int:friend_pk>/', AddNewFriend.as_view(), name='new_friend'),

]
