from django.utils import timezone
from django.forms.models import modelform_factory


class ModelBackend(object):
    def __init__(self, model_class):
        self.model_class = model_class

    def is_subscribed(self, email):
        return self.model_class.objects.filter(
            email=email,
            is_active=True,
        ).exists()

    def subscribe(self, email, ip_address, user_agent):
        subscription, created = self.model_class.objects.get_or_create(
            email=email,
        )
        if not subscription.is_active:
            subscription.is_active = True
            subscription.subscribe_confirmed_at = timezone.now()
            subscription.subscribe_confirmed_ip = ip_address
            subscription.subscribe_confirmed_user_agent = user_agent
            subscription.save()
            return True
        return False

    def unsubscribe(self, email):
        try:
            subscription = self.model_class.objects.get(email=email)
        except self.model_class.DoesNotExist:
            return

        subscription.is_active = False
        subscription.save()

    def subscription_details_form(self, email, request):
        try:
            instance = self.model_class.objects.get(email=email)
        except self.model_class.DoesNotExist:
            instance = None

        form_class = modelform_factory(
            self.model_class,
            exclude=('email', 'is_active', 'subscribe_confirmed_at', 'subscribe_confirmed_ip', 'subscribe_confirmed_user_agent'),
        )

        return form_class(request.POST or None, instance=instance)
