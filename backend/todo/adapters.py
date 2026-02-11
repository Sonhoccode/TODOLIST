from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.conf import settings
import traceback

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, exception=None, extra_context=None, **kwargs):
        print(f"!!! SOCIAL AUTH ERROR ({provider_id}) !!!")
        if exception:
            print(f"Exception: {exception}")
            traceback.print_exc()
        
        if extra_context:
            print(f"Extra Context: {extra_context}")
            
        super().authentication_error(request, provider_id, exception, extra_context, **kwargs)

    def save_user(self, request, sociallogin, form=None):
        print(f"!!! SAVING USER ({sociallogin.account.provider}) !!!")
        try:
            return super().save_user(request, sociallogin, form)
        except Exception as e:
            print(f"!!! ERROR SAVING USER: {e}")
            traceback.print_exc()
            raise e

    def pre_social_login(self, request, sociallogin):
        print(f"!!! PRE SOCIAL LOGIN ({sociallogin.account.provider}) !!!")
        print(f"User: {sociallogin.user}")
        print(f"Email: {sociallogin.user.email}")
        try:
            super().pre_social_login(request, sociallogin)
        except Exception as e:
            print(f"!!! ERROR PRE SOCIAL LOGIN: {e}")
            traceback.print_exc()
            raise e
