from users.utils import remove_expired_users_from_group

class ExpiredUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("custom middleware")
        print(request.user)
        user = request.user
        response = self.get_response(request)

        if user.is_authenticated:
            group_values = user.groups.values_list('name', flat=True)
            if 'subscribers' or 'admin' in group_values:
                remove_expired_users_from_group(user)

        return response