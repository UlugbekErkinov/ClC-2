from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from common.models import User
from datetime import timezone
from datetime import *
from channels.db import database_sync_to_async
# Create your models here.

STATUS = (('audio', 'audio'),
          ('video', 'video'),
          ('image', 'image'),
          ('emoji', 'emoji'),
          ('doument', 'document'))


class Chat(models.Model):
    # GROUP fields
    title = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="chat/", null=True, blank=True)

    members = models.ManyToManyField(User, related_name="chat")
    pinned = models.ManyToManyField(User, related_name='user_pinned')
    unmuted = models.ManyToManyField(User, related_name='user_unmuted')
    is_group = models.BooleanField(default=False)
    is_archived = models.ManyToManyField(User, related_name='user_archived')
    

class File(models.Model):
    file = models.FileField()
    massage = models.CharField(max_length=256, choices=STATUS)


class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    read = models.ManyToManyField(User, related_name='user_read')
    created_at = models.DateTimeField(auto_now_add=True)

class Notifications(models.Model):
    user_sender=models.ForeignKey(User,null=True,blank=True,related_name='user_sender',on_delete=models.CASCADE)
    user_revoker=models.ForeignKey(User,null=True,blank=True,related_name='user_revoker',on_delete=models.CASCADE)
    status=models.CharField(max_length=264,null=True,blank=True,default="unread")
    type_of_notification=models.CharField(max_length=264,null=True,blank=True)


@database_sync_to_async
def get_user(user_id):
    return User.objects.get(id=user_id)
    


@database_sync_to_async
def create_notification(receiver, typeof="task_created", status="unread"):
    notification_to_create = Notifications.objects.create(
        user_revoker=receiver, type_of_notification=typeof)
    print('I am here to help')
    return (notification_to_create.user_revoker.username, notification_to_create.type_of_notification)


@receiver(post_save, sender=Message)
def my_handler(sender, instance, created, **kwargs):
    """
    Send message to channel
    """
    channel_layer = get_channel_layer()
    if created:

        # YANGI XABAR BO'LSA
        async_to_sync(channel_layer.group_send)(
            "clc", {"type": "chat_message", "data": {
                "id": instance.id,
                "status": "new_message",
                "text": instance.text,
                "chat_id": instance.chat_id,
                "from_user_id": instance.from_user_id,
            }}
        )
    else:
        # UPDATE BO'LSA
        async_to_sync(channel_layer.group_send)(
            "clc", {"type": "chat_message", "data": {
                "id": instance.id,
                "status": "updated_message",
                "text": instance.text,
                "chat_id": instance.chat_id,
                "from_user_id": instance.from_user_id,
            }}
        )
