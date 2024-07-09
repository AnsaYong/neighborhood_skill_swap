from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse


from .forms import MessageForm
from .models import Message, SkillDeal


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


class MessageReadView(LoginRequiredMixin, View):
    """A view to mark a message as read."""

    def get(self, request, pk, *args, **kwargs):
        """Mark the message as read."""
        message = get_object_or_404(Message, pk=pk, receiver=request.user)

        # Mark the message as read
        if not message.is_read:
            message.is_read = True
            message.save()

        # Fetch the associated skill deal
        skill_deal = message.skill_deal

        context = {
            "message": message,
            "skill_deal": skill_deal,
        }
        return render(request, "skills/message_detail.html", context)


class MessageCreateView(LoginRequiredMixin, View):
    """A view to create a message for communication between users."""

    template_name = "skills/message_create.html"

    def get(self, request, pk, reply_to=None):
        """Render the message form."""
        form = MessageForm(initial={"reply_to": reply_to})
        skill_deal = get_object_or_404(SkillDeal, pk=pk)
        messages = Message.objects.filter(skill_deal=skill_deal).order_by("timestamp")
        context = {
            "form": form,
            "skill_deal_id": pk,
            "reply_to": reply_to,
            "skill_deal": skill_deal,
            "messages": messages,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk, reply_to=None):
        """Save the message form data to the database."""
        form = MessageForm(request.POST)
        if form.is_valid():
            skill_deal = get_object_or_404(SkillDeal, pk=pk)
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = (
                skill_deal.provider
                if request.user == skill_deal.owner
                else skill_deal.owner
            )
            message.skill_deal = skill_deal
            if reply_to:
                message.reply_to = get_object_or_404(Message, pk=reply_to)
            message.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "success": True,
                        "sender": message.sender.username,
                        "content": message.content,
                        "timestamp": message.timestamp.strftime("%b %d, %Y %H:%M"),
                    }
                )

            return redirect(reverse("skill_deal_detail", args=[pk]))

        # If form is invalid, render the form with errors
        skill_deal = get_object_or_404(SkillDeal, pk=pk)
        messages = Message.objects.filter(skill_deal=skill_deal).order_by("timestamp")
        context = {
            "form": form,
            "skill_deal_id": pk,
            "reply_to": reply_to,
            "skill_deal": skill_deal,
            "messages": messages,
        }
        return render(request, self.template_name, context)
