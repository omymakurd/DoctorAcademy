from django import template
register = template.Library()

@register.filter
def get_next_unit_id(current_id, units):
    units_list = list(units)
    for i, unit in enumerate(units_list):
        if unit.id == current_id and i + 1 < len(units_list):
            return units_list[i + 1].id
    return None
