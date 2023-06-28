from django.conf import settings

def get_khalti_api(request):
    return {'KHALTI_API_KEY':settings.KHALTI_API_KEY}