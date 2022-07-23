from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

from .models import *

# new_group, created = Group.objects.get_or_create(name="new_group")

# # Code to add permission to group ???
# ct = ContentType.objects.get_for_model(Project)

# # Now what - Say I want to add 'Can add project' permission to new_group?
# permission = Permission.objects.create(
#     codename="can_add_project", name="Can add project", content_type=ct
# )
# new_group.permissions.add(permission)


def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name="customer")
        instance.groups.add(group)
        Customer.objects.create(user=instance, name=instance.username)
        print("Profile Created !!")


post_save.connect(customer_profile, User)
