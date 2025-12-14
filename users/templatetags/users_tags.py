from django import template
register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_names):
    if user.is_anonymous:
        return False
    group_list = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()
