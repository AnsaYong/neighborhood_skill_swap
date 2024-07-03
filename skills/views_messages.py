from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Message


class MessageListView(LoginRequiredMixin, ListView):
    """A view to display the list of messages for the logged-in user.

    Attributes:
        model: A model to represent the message notification regarding a swap deal.
        template_name: A string to represent the name of the template.
        context_object_name: A string to represent the context object name.
        paginate_by: An integer to represent the number of items to display per page.
    """

    model = Message
    template_name = "skills/messages_list.html"
    context_object_name = "messages"
    paginate_by = 10

    def get_queryset(self):
        """Filter messages for the logged-in user."""
        return Message.objects.filter(receiver=self.request.user).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        """Mark messages as read."""
        context = super().get_context_data(**kwargs)
        # Mark messages as read
        unread_messages = Message.objects.filter(
            receiver=self.request.user, is_read=False
        )
        unread_messages.update(is_read=True)
        return context
