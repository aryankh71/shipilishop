from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, CustomerProfile


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):

    if created and instance.role == User.Role.CUSTOMER:
        CustomerProfile.objects.create(
            user=instance
        )


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):

    if instance.role == User.Role.CUSTOMER:
        if hasattr(instance, "profile"):
            instance.profile.save()