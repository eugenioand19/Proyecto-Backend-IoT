def json_structure_error(code,message="", details=""):
    return{ 
                    "data": [], 
                    "errors": 
                { 
                    "code":code,
                    "message": str(details)
                },
                   "message": message
            
            
        },code

def json_structure_ok(data,message,code):
    return{ 
                    "data": data, 
                     "errors": 
                { 
                    "code":code,
                    "message": "Sucess!"
                },
                   "message": message
            
            
        },code

def json_structure_pagination(total,total_pages,current_page,per_page, code = 200, message="Sucess.",data={}):
    return {
    "paging": {
        "total_count": total,
        "total_pages": total_pages,
        "current_page": current_page,
        "per_page": per_page    
    },
    "data": data,
    "errors": 
                { 
                    "code":code,
                    "message": message
                    
                }
},code