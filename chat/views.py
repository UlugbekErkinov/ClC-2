from distutils.util import change_root
from django.shortcuts import render
from rest_framework import generics
# Create your views here.
from django.db import models
from chat.models import Chat, Message
from common.models import User
from chat import serializers
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer




class ChatListView(generics.ListAPIView):

    
    queryset = Chat.objects.all().annotate(
        last_message=Message.objects.filter(
            chat_id=models.OuterRef('id')).order_by('-created_at').values('text')[:1],
        last_message_date=Message.objects.filter(
            chat_id=models.OuterRef('id')).order_by('-created_at').values('created_at')[:1]
    )
    serializer_class = serializers.ChatListSerializer
# .order_by("-messages__created_at").distinct()

    def get_queryset(self, request):

        # if request.method == "POST":
        #     vars["created_ad"] = request.POST.get("desc")
        # print(vars["created_at"])

        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     f'chat_{id}',
        #     {
        #         'type': 'receive',
        #         'message': last_message
        #     }
        # )
        # Message.objects.filter(read = User.objects.exclude(id = self.request.user.id).filter(chat_id =   ))

        return self.queryset.filter(members=self.request.user).annotate(
            # profile image
            profile_image=models.Case(
                models.When(is_group=True, then=models.F('avatar')),
                models.When(is_group=False, then=User.objects.exclude(
                    id=self.request.user.id).filter(chat__title=models.OuterRef('title')).values('avatar')[:1]),
                default=models.Value('None image'),
                output_field=models.CharField()

            ),
            # profile title
            profile_title=models.Case(
                models.When(is_group=True, then=models.F('title')),
                models.When(is_group=False, then=User.objects.exclude(
                    id=self.request.user.id).filter(chat__title=models.OuterRef('title')).values('full_name')[:1]),
                default=models.Value('None image')

            ),
            is_unmuted=models.Case(
                models.When(unmuted=self.request.user, then=True),
                default=False,
                output_field=models.BooleanField()
            ),
            
            message_count=Message.objects.filter(chat__members=User.objects.get(id=self.request.user.id)).filter(
                read=User.objects.exclude(id=self.request.user.id)).count(),




        ).order_by("-messages__created_at", "-pinned")[:1]
