from rest_framework import validators


def positive_integer_in_field_validate(value, field_name):
    if not isinstance(value, int):
        raise validators.ValidationError(f"{field_name} must be an integer.")
    if value < 1:
        raise validators.ValidationError(
            f"{field_name} must be positive integer."
        )
    return value


def unique_in_query_params_validate(items, field_name, value):
    items_quantity = len(items)
    unique_items_quantity = len(set(items))
    if items_quantity > unique_items_quantity:
        raise validators.ValidationError(
            f"You can not add a specific {field_name} to a specific recipe more than once."
        )
    return value


def object_exists_validate(data, context, model, location):
    if model.objects.filter(user=context["request"].user, recipe=data["recipe"]).exists():
        raise validators.ValidationError(
            f"You have already added this recipe in your {location}."
        )
    return data
