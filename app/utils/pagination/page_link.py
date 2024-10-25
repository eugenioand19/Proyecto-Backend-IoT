import re


class ThingsboardException(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code


class SortOrder:
    ASC = "ASC"
    DESC = "DESC"

    def __init__(self, property_name, direction):
        if direction not in [SortOrder.ASC, SortOrder.DESC]:
            raise ValueError(f"Invalid sort order '{direction}'! Only 'ASC' or 'DESC' types are allowed.")
        self.property_name = property_name
        self.direction = direction


class PageLink:
    def __init__(self, page_size, page, text_search=None, sort_order=None):
        self.page_size = page_size
        self.page = page
        self.text_search = text_search
        self.sort_order = sort_order

class TimePageLink:
    def __init__(self, page_link, start_time, end_time):
        self.page_link = page_link
        self.start_time = start_time
        self.end_time = end_time

def create_page_link(page_size, page, text_search=None, sort_property=None, sort_order=None):
    
    if sort_property:
        if not is_valid_property(sort_property):
            raise ValueError("Invalid sort property")
        
        direction = SortOrder.ASC
        if sort_order:
            sort_order = sort_order.upper()
            if sort_order not in [SortOrder.ASC, SortOrder.DESC]:
                raise ThingsboardException(f"Unsupported sort order '{sort_order}'! Only 'ASC' or 'DESC' types are allowed.", 'BAD_REQUEST_PARAMS')

            direction = sort_order

        sort = SortOrder(sort_property, direction)
        return PageLink(page_size, page, text_search, sort)
    
    return PageLink(page_size, page, text_search)

def create_time_page_link(page_size, page, text_search, sort_property, sort_order, start_time, end_time):
    try:
        page_link = create_page_link(page_size, page, text_search, sort_property, sort_order)
        return TimePageLink(page_link, start_time, end_time)
    except Exception as e:
        raise ThingsboardException(f"Error while creating TimePageLink: {str(e)}")

def is_valid_property(property_name):
    # Validate if the string matches the regex (Unicode characters, numbers, '_', '-')
    return not property_name or re.match(r'^[\w-]+$', property_name, re.UNICODE)

