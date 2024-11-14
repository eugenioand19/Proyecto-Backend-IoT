from marshmallow import Schema, fields, validate


class WetlandSchema(Schema):
    name = fields.String(required=True)

class NodeSchema(Schema):
    name = fields.String(required=True)
class SensorSchema(Schema):
    register_date = fields.String()
    value = fields.String()
    type_sensor = fields.String()
    unity = fields.String()

class ReportSchema(Schema):
    wetland = fields.Nested(WetlandSchema)
    node = fields.Nested(NodeSchema)
    sensor = fields.Nested(SensorSchema)

class ReportQuerySchema(Schema):
    page_size = fields.Int(required=True, description="Page size", validate=validate.Range(min=1))
    page = fields.Int(required=True, description="Page number", validate=validate.Range(min=1))
    sort_property = fields.Str(required=False, description="Sort property", 
                               validate=validate.OneOf(["register_date","node_name","wetland_name","data_history_value","sensor_name"]))
    sort_order = fields.Str(required=False, description="Sort order", 
                            validate=validate.OneOf(["ASC", "DESC"]))
    start_time = fields.Str(required=False, description="Star date")
    end_time = fields.Str(required=False, description="End date")
    sensor_type = fields.Str(required=False, description="Filter with typer sensor")
