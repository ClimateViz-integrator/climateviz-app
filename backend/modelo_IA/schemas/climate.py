from pydantic import BaseModel

class Climate(BaseModel):
    city : str
    region : str
    country : str
    lat : float
    lon : float
    temp_f : float
    temp_c : float
    localtime : str
    


    input_id : int