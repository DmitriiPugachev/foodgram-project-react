from rest_framework import serializers, validators


def positive_integer_in_field_validate(value, field_name):
    if not isinstance(value, int):
        raise serializers.ValidationError(
            f"{field_name} must be an integer."
        )
    if value < 1:
        raise serializers.ValidationError(
            f"{field_name} must be positive integer."
        )
    return value


def object_exists_validate(data, object_name, object_exists, location):
    if object_exists:
        raise validators.ValidationError(
            f"You have already added this {object_name} in your {location}."
        )
    return data
