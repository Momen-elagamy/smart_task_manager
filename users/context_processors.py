def show_add_member_link(request):
    """Context processor that exposes whether current user can add members.

    Returns a boolean `show_add_member_link` that's true for superusers
    or users in the Admin or Manager groups.
    """
    user = getattr(request, 'user', None)
    if not user or user.is_anonymous:
        return {'show_add_member_link': False}
    try:
        allowed = user.is_superuser or user.groups.filter(name__in=['Admin', 'Manager']).exists()
    except Exception:
        allowed = False
    return {'show_add_member_link': bool(allowed)}
