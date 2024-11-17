from marshmallow import Schema, ValidationError, fields

class DelimitedListField(fields.Field):
    def __init__(self, *args, **kwargs):
        self.allowed_values = kwargs.pop('allowed_values', [])
        super().__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise ValidationError(f"{attr} must be a string, received {type(value).__name__}.")
        
        # Split the string into a list
        items = [item.strip() for item in value.split(",")]
        
        # Apply validation to each item in the list
        if self.allowed_values:
            for item in items:
                if item not in self.allowed_values:
                    raise ValidationError(f"'{item}' is not a valid value for {attr}. Must be one of {self.allowed_values}.")
                #raise CustomException("Sorry, no numbers below zero",status_code=404)
        
        return items