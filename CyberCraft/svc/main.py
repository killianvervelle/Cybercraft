import os
import sys
import logging
import itertools
import pandas as pd
from typing import Optional
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from fuzzywuzzy import fuzz
from task import *
from scrappy import *

from optimizer import Optimizer


# *****************************************************************************
#                  Some global constants and variables
# *****************************************************************************


NAME = 'CyberCraft'
VERSION = '1.1.9'
DESCRIPTION = "CyberCraft was designed to build computer configurations with the best cost to performance ratio. It takes as \
    input component data scrapped on the internet and the user's requirements."
SCRAP_PATH: str = 'data/'
URL_PREFIX: str = os.getenv("URL_PREFIX") or ""
SERVER_ADDRESS: str = os.getenv("SERVER_ADDRESS") or ""


# *****************************************************************************
#                  FastAPI entry point declaration
# *****************************************************************************


rootapp = FastAPI()

app = FastAPI(openapi_url='/specification')
app.add_middleware(CORSMiddleware, allow_origins=["*"], 
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=NAME, version=VERSION, 
        description=DESCRIPTION, routes=app.routes,)
    openapi_schema["info"]["x-logo"] = {"url": "assets/digirent-logo.png"}
    if SERVER_ADDRESS != "":
        openapi_schema["servers"] = [
            {"url": "http://digirent-ai.kube.isc.heia-fr.ch/" + URL_PREFIX, 
            "description": "MS to predict best pub. strategy for a property."}
        ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
rootapp.mount(URL_PREFIX, app)
logger = logging.getLogger("uvicorn.error")
logger.info('Starting app with URL_PREFIX=' + URL_PREFIX)


# *****************************************************************************
#                  Set the logging for the service
# *****************************************************************************


logger = logging.getLogger("uvicorn.error")
logger.info('Starting app with URL_PREFIX=' + URL_PREFIX)


# ******************************************************************************
#             Classes declaration - for input and output models
# ******************************************************************************


class parameters(BaseModel):
    budget: Optional[int] = None
    cpu_brand: Optional[str] = None
    gpu_brand: Optional[str] = None
    gpu_mem: Optional[int] = None
    ram_brand: Optional[str] = None
    ram_sticks: Optional[int] = None
    ram_capa: Optional[int] = None
    ssd_brand: Optional[str] = None
    ssd_capa: Optional[int] = None
    mother_brand: Optional[str] = None


# *****************************************************************************
#                  Done once when micro-service is starting up
# *****************************************************************************


@rootapp.on_event("startup")
def initialization():
    cpu = pd.read_csv("data/clean/merged/CPU.csv")
    gpu = pd.read_csv("data/clean/merged/GPU.csv")
    ram = pd.read_csv("data/clean/merged/RAM.csv")
    ssd = pd.read_csv("data/clean/merged/SSD.csv")
    case = pd.read_csv("data/raw/case.csv")
    power = pd.read_csv("data/raw/power.csv")
    mb = pd.read_csv("data/raw/mb.csv")
    rad = pd.read_csv("data/raw/rad.csv")
    
    power['power'] = power['power'].str.replace('W', '').astype('float')
    case['len_gpu_max'] = case['len_gpu_max'].str.replace('mm', '').astype('float')
    rad['largeur'] = rad['largeur'].str.replace('mm', '').astype('float')
    
    return gpu, cpu, ssd, ram, power, case, rad, mb
    

# ******************************************************************************
#                  API Route definition
# ******************************************************************************


@app.get("/")
def info():
    return {'message': 'Welcome to CyberCraft, your very own personal computer configurator. Try out /showcase for the showcase and /docs for the doc.'}

@app.post("/build")
async def build(params: parameters):
    global budget
    gpu, cpu, ssd, ram, power, case, rad, mb = initialization()
    
    # Setting the user budget as a variable
    if params: 
        logger.info('User requirements received')
    else: 
        raise logger.error("Failed to import the user's requirements")
    budget = params.budget
    cpu_brand = params.cpu_brand
    gpu_brand = params.gpu_brand
    gpu_mem = params.gpu_mem
    ram_brand = params.ram_brand
    ram_sticks = params.ram_sticks
    ram_capa = params.ram_capa
    ssd_brand = params.ssd_brand
    ssd_capa = params.ssd_capa
    mother_brand = params.mother_brand
    
    # Filtering the data files from the user's requirements
    cpu = cpu[cpu['brand'] == cpu_brand] if cpu_brand != "All" else cpu
    gpu = gpu[gpu['brand'] == gpu_brand] if gpu_brand != "All" else gpu
    gpu = gpu[gpu['memory'] >= gpu_mem] if gpu_mem != 0 else gpu
    ram = ram[ram['Brand'] == ram_brand] if ram_brand != "All" else ram
    ram = ram[ram['Number of sticks'] >= ram_sticks] if ram_sticks != 0 else ram
    ram = ram[ram['Capacity of each stick'] >= ram_capa] if ram_capa != 0 else ram
    ssd = ssd[ssd['Brand'] == ssd_brand] if ssd_brand != "All" else ssd
    ssd = ssd[ssd['memory'] >= ssd_capa] if ssd_capa != 0 else ssd
    mb = mb[mb['name'].str.contains(mother_brand)] if mother_brand != "All" else mb

    # Selecting components from the user's budget, share was performed arbitrarily
        
    # Find the main components
    max_budget = budget * 0.7
    optimizer = Optimizer(max_budget)
    optimizer.from_dataframes(cpu, gpu, ram, ssd)
    cpu, gpu, ram, ssd = optimizer.optimize()
    if cpu is None:
        return {f"No mains parts found, please readjust requirements or increase budget."}
    
    # Find the others components
    components = {
    'mb': (mb, 0.1),
    'power': (power, 0.1),
    'rad': (rad, 0.05),
    'case': (case, 0.05)
    }
    
    for component, (df, threshold) in itertools.islice(components.items(), len(components)):
        try:
            df = listing(df, budget, threshold)
        except Exception as e:
            return {f"No {component} found, please readjust requirements or increase budget."}

    # Processing the compatibility and building the final setup
    try:
        mb, power, rad, case = compatibility(case, mb, rad, power, gpu, ram, budget)
    except Exception as e:
        return {"Compatibility testing failed."}
    
    # Scrapping the top priced supplier URLs
    arg = [gpu["model"].iloc[0], cpu["model"].iloc[0], ssd["model"].iloc[0], ram["model"].iloc[0], mb, power, rad, case]
    scrapp_latest_prices(arg)
    
    # Build the response returned to the user
    config = pd.read_csv('config.csv').drop(['url'], axis=1)
    config['name'] = config['name'].str[:25]
    config['type'] = config['type'].str\
        .replace("Cartes graphiques & accessoires", "Carte graphique")\
        .replace("Processeurs", "Processeur")\
        .replace("Disques durs & SSD", "Disque dur & SSD")\
        .replace("Refroidissement par eau", "Refroidissement")\
        .replace("Cartes mères", "Carte mère")\
        .replace("Boîtiers & alimentation", "Boîtier & alimentation") 
    response = {}
    ite = 0
    while ite < 8:
        try:
            response[f"component{ite+1}"] = config.iloc[[ite]].to_json(orient='records')
        except:
            print(f"Item {ite+1} does not exist in the config file.")
            response[f"component{ite+1}"] = "Process failed to select this component."
        ite +=1
    return response

@app.get("/showcase")
def showcase():
    """
    Showcase website demonstrating the functionalities of the microservice.
    :return: HTML
    """
    logger.info("route '/showcase' called")

    return FileResponse(os.path.dirname(os.getcwd())+"/showcase/index.html")

@app.get("/assets/{filename}")
async def assets(filename: str):
    logger.info("route '/assets/{}' called".format(filename))

    return FileResponse(os.path.dirname(os.getcwd())+ "/showcase/assets/" + filename)


# ******************************************************************************
#                  API Functions
# ******************************************************************************
 
 
def scrapp_latest_prices(arg):
    # Runs once to retrieve all benchmark
    process = CrawlerProcess(settings={
            "FEEDS": {
                "config.csv": {"format": "csv", "overwrite": True}
            },
            "LOG_LEVEL" : 'DEBUG',
            'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
            "arg" : arg
        })  
    try:
        # Start the Scrapy crawler
        process.crawl(QuotesSpider)
        process.start()
    except:
        # Catch KeyboardInterrupt and perform cleanup
        process.stop()
        process.join()
        
# function to find the closest match between two strings
def find_closest_match(x, choices):
    return max(choices, key=lambda y: fuzz.ratio(x, y) if x and y else "No match found")

def partial_ratio_1(x, y):
    return fuzz.partial_ratio(x, y, score_cutoff=1)

# function to find the best match
def listing(df, budget, factor):
    return df[df['price'] < budget*factor].sort_values(by="price", ascending=False).reset_index(drop=True)

# function to check the compatibility between pairs of hardwares and returns the selected component
def compatibility(case, mb, rad, power, gpu, ram, budget):
    choice_case = 0
    choice_mb = 0
    choice_power = 0
    choice_rad = 0

    # Selecting motherboard with budget and memory type as constraints
    while mb["memory_type"].iloc[choice_mb] not in ram["model"].iloc[0] \
          or mb["price"].iloc[choice_mb] > budget * 0.1:
            choice_mb +=1

    # Selecting power supply with budget and gpu power usage as constraints
    while power["power"].iloc[choice_power] < gpu["power_usage"].iloc[0] \
          or power["price"].iloc[choice_power] > budget * 0.1:
            choice_power +=1

    # Selecting cooling system with budget as constraint
    rad = rad.iloc[[choice_rad]]

    # Selecting case with budget, gpu length, rad length and motherboard type as constraints
    while case["len_gpu_max"].iloc[choice_case] < rad["largeur"].iloc[choice_rad] \
          or case["len_gpu_max"].iloc[choice_case] < gpu["length"].iloc[0]\
          or (mb["format"].iloc[choice_mb] != case["type_mb1"].iloc[choice_case] \
          and mb["format"].iloc[choice_mb] != case["type_mb2"].iloc[choice_case]):
            choice_case += 1 
    
    return  mb["name"].iloc[choice_mb], \
            power["name"].iloc[choice_power], \
            rad["name"].iloc[choice_rad], \
            case["name"].iloc[choice_case], 