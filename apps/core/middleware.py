from django.utils import timezone, translation
import pytz


class UserLangMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = self.get_language(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        if hasattr(request, 'user') and request.user.is_authenticated:
            user_tz = pytz.timezone(request.user.user_timezone)
            timezone.activate(user_tz)
        else:
            timezone.deactivate()


        response = self.get_response(request)
        return response

    def get_language(self, request):
        supported = ['en', 'ru', 'kk']

        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.preferred_language in supported:
                return request.user.preferred_language

        lang = request.GET.get('lang')
        if lang in supported:
            return lang

        accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for lang_code in supported:
            if lang_code in accept_lang:
                return lang_code

        return 'en'