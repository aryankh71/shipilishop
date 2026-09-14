from decimal import Decimal

from django import template


register = template.Library()


@register.filter
def price_format(value):

    if value is None:
        return ""

    try:

        value = Decimal(value)

    except (
        ValueError,
        TypeError,
    ):

        return value


    # اگر قیمت اعشاری ندارد، .00 نمایش داده نشود
    if value == value.to_integral_value():

        return f"{int(value):,}"


    # اگر واقعاً بخش اعشاری دارد
    return f"{value:,}"