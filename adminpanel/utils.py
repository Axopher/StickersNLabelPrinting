from users.models import Payment,Profile
from django.core.paginator import Paginator, PageNotAnInteger,EmptyPage

def paginateProfiles(request,payments,results):
    # Paginate the payments
    page = request.GET.get('page')
    paginator = Paginator(payments, results)  # Adjust the number of payments per page as needed

    try:
        payments = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        payments = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        payments = paginator.page(page)    

    leftIndex = (int(page) - 4)
    if leftIndex < 1:
        leftIndex = 1
    
    rightIndex = (int(page) + 5)   
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex,rightIndex)

    return custom_range,payments

