from pydantic import BaseModel
from cat.mad_hatter.decorators import plugin

class MySettings(BaseModel):
    api_key: SecretStr
    curiosity: bool=True
    language: str ="Italian"

@plugin
def settings_schema():
    return MySettings.schema()
