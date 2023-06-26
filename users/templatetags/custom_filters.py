from django import template

register = template.Library()

@register.filter
def get_subscription_by_name(queryset, name):
    subscription = queryset.filter(plan=name).first()
    return subscription

@register.filter
def get_subscription_duration(subscription):
    return subscription.get_duration()
