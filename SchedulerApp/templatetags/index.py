from django import template

register = template.Library()


@register.filter(name='dictKey')
def dict_key(mapping, key):
    """Return a joined string for the requested dictionary key."""
    values = mapping.get(key)
    return ', '.join(values) if values else ''


@register.simple_tag(name='sub')
def subject_for_slot(schedule_items, group_code, weekday, period):
    """Return the subject and instructor associated with a time slot."""
    from django.utils.safestring import mark_safe
    for item in schedule_items:
        if (
            item.group.group_code == group_code
            and item.time_slot.weekday == weekday
            and item.time_slot.duration == period
        ):
            teacher_text = item.teacher.full_name if item.teacher else 'TBA'
            return mark_safe(
                f'<div class="subject">{item.subject.subject_title}</div>'
                f'<div class="lecture">({teacher_text})</div>'
            )

    return ''


@register.tag(name='active')
def active(parser, token):
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError(
            f'{tokens[0]} tag requires at least one argument'
        )
    return NavSelectedNode(tokens[1:])


class NavSelectedNode(template.Node):
    def __init__(self, patterns):
        self.patterns = patterns

    def render(self, context):
        current_path = context['request'].path
        for pattern in self.patterns:
            resolved = template.Variable(pattern).resolve(context)
            if current_path == resolved:
                return 'active'
        return ''
