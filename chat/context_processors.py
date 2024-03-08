from django.shortcuts import reverse


def back_url(request):
    url = request.META.get('HTTP_REFERER', reverse('home'))
    return {'back_url': url}
