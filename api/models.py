from django.db import models
from django.contrib.auth.models import User




class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_history")
    question = models.TextField()
    answer = models.TextField()
    references = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Correction(models.Model):
    chat = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name="corrections")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correction by {self.user} on {self.chat.id}"

class Feedback(models.Model):
    VOTE_CHOICES = (
        (1, 'Useful'),
        (-1, 'Not Useful'),
    )
    chat = models.ForeignKey(ChatHistory, on_delete=models.CASCADE, related_name="feedback")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')  

    def __str__(self):
        return f"Feedback from {self.user} on {self.chat.id}: {self.vote}"


