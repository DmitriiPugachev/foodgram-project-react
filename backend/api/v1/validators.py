from rest_framework import serializers, validators


def positive_integer_in_field_validate(value, field_name):
    if not isinstance(value, int):
        raise serializers.ValidationError(f"{field_name} must be an integer.")
    if value < 1:
        raise serializers.ValidationError(
            f"{field_name} must be positive integer."
        )
    return value


def object_exists_validate(data, context, model, location):
    if model.objects.filter(user=context["request"].user, recipe=data["recipe"]).exists():
        raise validators.ValidationError(
            f"You have already added this recipe in your {location}."
        )
    return data
