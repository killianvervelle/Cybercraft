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
    ram_price = pd.read_csv("data/clean/LDLC/RAM.csv")
    ram_bench = pd.read_csv("data/clean/UserBenchmarks/RAM.csv")
    ssd_price = pd.read_csv("data/clean/LDLC/SSD.csv")
    ssd_bench = pd.read_csv("data/clean/UserBenchmarks/SSD.csv")
    cpu_price = pd.read_csv("data/clean/LDLC/CPU.csv")
    cpu__bench = pd.read_csv("data/clean/UserBenchmarks/CPU.csv")
    gpu_raw = pd.read_csv("data/raw/GPU.csv")
    gpu_price = pd.read_csv("data/clean/LDLC/GPU.csv")
    gpu__bench = pd.read_csv("data/clean/UserBenchmarks/GPU.csv")
    case = pd.read_csv("data/raw/case.csv")
    power = pd.read_csv("data/raw/power.csv")
    mb = pd.read_csv("data/raw/mb.csv")
    rad = pd.read_csv("data/raw/rad.csv")
    
    gpu_raw['price'] = gpu_raw['price'].str.replace("'", "").astype('float')
    gpu__bench['Model'] = gpu__bench['Model'].str.replace('-', ' ')
    power['power'] = power['power'].str.replace('W', '').astype('float')
    case['len_gpu_max'] = case['len_gpu_max'].str.replace('mm', '').astype('float')
    rad['largeur'] = rad['largeur'].str.replace('mm', '').astype('float')
    
    gpu = pd.merge(gpu_price, gpu__bench, on='Model')
    cpu = pd.merge(cpu_price, cpu__bench, on='Model')
    ssd = pd.merge(ssd_price, ssd_bench, on='Model')
    ram = pd.merge(ram_price, ram_bench, on='Part Number')
    
    # Merging csv files to retain compatiblity characteristics
    terms = [term for term in gpu["Model"]]
    split_terms = [term.split() for term in terms]
    flattened_terms = [term for sublist in split_terms for term in sublist]
    
    # Filter out none key terms for gpu name
    gpu_raw['name'] = gpu_raw['name'].apply(lambda x: ' '.join([word for word in x.split() if word in flattened_terms]))  
    merged_gpu = gpu_raw.merge(gpu, left_on='name', right_on='Model').drop(columns=["model", "Brand_y", "price_y"]).rename(columns={'price_x': 'price', 'Brand_x': 'brand'})
    cpu = cpu.drop(columns=["Brand_y"]).rename(columns={'Brand_x': 'brand'})
    # agg max on power usage and length as a security margin
    merged_gpu = merged_gpu.groupby('Model').agg({'brand':'first','power_usage': 'max', 'length': 'max', 'Memory': 'mean', 'Benchmark': 'mean', 'price': 'mean'}).sort_values(by='Benchmark').reset_index()
    
    # removing mm and w from power and length for futur calculations
    merged_gpu['power_usage'] = merged_gpu['power_usage'].str.replace('W', '').astype('int')
    merged_gpu['length'] = merged_gpu['length'].str.replace('mm', '').astype('float')
    return merged_gpu, cpu, ssd, ram, power, case, rad, mb
    

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
    gpu = gpu[gpu['Memory'] >= gpu_mem] if gpu_mem != 0 else gpu
    ram = ram[ram['Brand'] == ram_brand] if ram_brand != "All" else ram
    ram = ram[ram['Number of sticks'] >= ram_sticks] if ram_sticks != 0 else ram
    ram = ram[ram['Capacity of each stick'] >= ram_capa] if ram_capa != 0 else ram
    ssd = ssd[ssd['Brand'] == ssd_brand] if ssd_brand != "All" else ssd
    ssd = ssd[ssd['Memory'] >= ssd_capa] if ssd_capa != 0 else ssd
    mb = mb[mb['name'].str.contains(mother_brand)] if mother_brand != "All" else mb

    # Selecting components from the user's budget, share was performed arbitrarily
    
    components = {
    'gpu': (gpu, budget * 0.3),
    'cpu': (cpu, budget * 0.2),
    'ssd': (ssd, budget * 0.1),
    'ram': (ram, budget * 0.1),
    'mb': (mb, 0.1),
    'power': (power, 0.1),
    'rad': (rad, 0.1),
    'case': (case, 0.03)
    }

    for component, (df, threshold) in itertools.islice(components.items(), 4):
        try:
            df = unit(df[df['price'] < threshold])
        except Exception as e:
            return {f"No {component} found, readjust requirements or increase budget."}
    
    for component, (df, threshold) in itertools.islice(components.items(), 4, 8):
        try:
            df = listing(df, budget, threshold)
        except Exception as e:
            return {f"No {component} found, readjust requirements or increase budget."}

    # Processing the compatibility and building the final setup
    try:
        mb, power, rad, case = compatibility(case, mb, rad, power, gpu, ram, budget)
    except Exception as e:
        return {"Compatibility testing failed."} 
    
    # Scrapping the top priced supplier URLs
    arg = [gpu.at[0,'Model'], cpu.at[0,'Model'], ssd.at[0,'Model'], ram.at[0,'Model'], mb, power, rad, case]
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
def unit(df):
    return df[df['Benchmark'] == df['Benchmark'].max()].sort_values(by="price").iloc[[0]].reset_index(drop=True)

def listing(df, budget, factor):
    return df[df['price'] < budget*factor].sort_values(by="price", ascending=False).reset_index(drop=True)

# function to check the compatibility between pairs of hardwares and returns the selected component
def compatibility(case, mb, rad, power, gpu, ram, budget):
    choice_case = 0
    choice_mb = 0
    choice_power = 0
    choice_rad = 0

    # Selecting motherboard with budget and memory type as constraints
    while mb.at[choice_mb,"memory_type"] not in ram.at[0,"Model"] \
          or mb.at[choice_mb,"price"] > budget * 0.1:
            choice_mb +=1
    
    # Selecting power supply with budget and gpu power usage as constraints
    while power.at[choice_power,"power"] <  gpu.at[0,"power_usage"] \
          or power.at[choice_power,"price"] > budget * 0.1:
            choice_power +=1

    # Selecting cooling system with budget as constraint
    rad = rad.iloc[[choice_rad]]

    # Selecting case with budget, gpu length, rad length and motherboard type as constraints
    while case.at[choice_case,"len_gpu_max"] <  rad.at[choice_rad,"largeur"] \
          or case.at[choice_case,"len_gpu_max"] < gpu.at[0,"length"] \
          or (mb.at[choice_mb,"format"] != case.at[choice_case,"type_mb1"] \
          and mb.at[choice_mb,"format"] != case.at[choice_case,"type_mb2"]):
            choice_case += 1 
    
    return  mb.at[choice_power,"name"], \
            power.at[choice_power,"name"], \
            rad.at[choice_power,"name"], \
            case.at[choice_power,"name"], 