from marshmallow import Schema, ValidationError, fields, validate
from flask_marshmallow.sqla import SQLAlchemyAutoSchema
from app.models.wetland import Wetland


class WetlandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Wetland
        load_instance = True

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
        for item in items:
            if item not in self.allowed_values:
                raise ValidationError(f"'{item}' is not a valid value for {attr}. Must be one of {self.allowed_values}.")
                #raise CustomException("Sorry, no numbers below zero",status_code=404)
        
        return items

class WetlandQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    text_search = fields.Str(required=False, description="Search query")
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["created_at", "status", "name", "location"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))

    valid_statuses = ["CRITIC","GOOD","NORMAL"]

    # Passing the list of allowed values for validation
    statusList = DelimitedListField(
        allowed_values=valid_statuses,
        required=False,
        description="Comma-separated list of status values."
    )