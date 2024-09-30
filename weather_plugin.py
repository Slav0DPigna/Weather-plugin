import requests
from pydantic import BaseModel, Field
from cat.experimental.form import form, CatForm
from cat.looking_glass.prompts import MAIN_PROMPT_PREFIX
import json

def get_weather(city_name, country,api_key):
    # URL base dell'API OpenWeatherMap per la richiesta
    base_url = "https://api.openweathermap.org/data/2.5/weather?"

    # Parametri della richiesta
    params = {
        'q': city_name+","+ country,
        'appid': api_key,
        'units': 'metric',  # Usa 'imperial' per i gradi Fahrenheit
        'lang': 'it'        # Per ottenere la risposta in italiano
    }

    # Invia la richiesta HTTP GET
    response = requests.get(base_url, params=params)
    return response.json()

class Weather(BaseModel):
    city: str= Field(description="Una cittá per controllare il meteo attuale")
    country: str= Field(description="le iniziali della nazione in maiuscolo di cui fa parte la cittá per controllare il meteo")

@form
class Weather_form(CatForm):
    description = "Check weather infromation for a given location"
    model_class = Weather
    start_examples = [
        "Che tempo fa",
        "Dimmi il meteo"
    ]
    stop_examples = [
        "Non lo voglio sapere piú",
        "Fermati",
        "stop"
    ]
    ask_confirm = False

    def get_prefix(self):
        prefix = self.cat.mad_hatter.execute_hook(
            "agent_prompt_prefix",
            MAIN_PROMPT_PREFIX,
            cat=self.cat
            )
        return prefix

    def submit(self, form_data):
        settings = self.cat.mad_hatter.get_plugin().load_settings()
        api_key= settings["api_key"]
        curiosity= settings["curiosity"]
        language= settings["language"]

        contex=self.get_prefix() +"""Quello che segue é un json che contiene le informazioni meteo di una cittá,
                                     riferiscimi e interpreta le informazioni riguardo il meteo ometti le altre, 
                                     rispondi in """
        contex=contex+language+"."
        curiosity_promtp="Prima di finire racconta sempre un aneddoto interessante sul meteo."
        prompt=contex + json.dumps(get_weather(form_data['city'],form_data['country'],api_key))
        if curiosity:
            tmp=self.cat.llm(prompt + curiosity_promtp,stream=True)
        else:
            tmp = self.cat.llm(prompt, stream=True)
        return {"output": tmp}
