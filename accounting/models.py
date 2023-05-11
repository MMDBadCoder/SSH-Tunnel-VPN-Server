from django.contrib.auth.models import User


def get_first_name(self):
    return self.first_name


User.add_to_class("__str__", get_first_name)
