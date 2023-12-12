import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^[a-zA-Z]+\/(...)\/(....)'
    message = _(
        'Yaroqli foydalanuvchi nomini kiriting. Bu qiymat faqat ingliz harflarini o\'z ichiga olishi mumkin, '
        'raqamlar va @/./+/-/_ belgilar.'
    )
    flags = re.ASCII
