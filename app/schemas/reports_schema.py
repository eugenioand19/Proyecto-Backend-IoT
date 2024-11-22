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
    page_size = fields.Int(required=False, description="Page size")
    page = fields.Int(required=False, description="Page number")
    start_time = fields.Str(required=False, description="Star date")
    end_time = fields.Str(required=False, description="End date")
    sensor_type = fields.Str(required=False, description="Filter with typer sensor")
    format = fields.Str(required=False, description="Formato")

class ReportGraphQuerySchema(Schema):
    start_time = fields.Str(required=True, description="Star date")
    end_time = fields.Str(required=True, description="End date")

