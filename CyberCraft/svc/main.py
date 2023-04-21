import os
import logging
import pandas as pd
from celery import Celery
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from fuzzywuzzy import fuzz
from task import *
from scrappy import *
from flask import Flask, jsonify


# *****************************************************************************
#                  Some global constants and variables
# *****************************************************************************


NAME = 'CyberCraft'
VERSION = '1.1.0'
DESCRIPTION = "CyberCraft was designed to build computer configurations with the best cost to performance ratio. It takes as \
    input component data scrapped on the internet and the user's requirements."
SCRAP_PATH: str = 'data/'
URL_PREFIX: str = os.getenv("URL_PREFIX") or ""
SERVER_ADDRESS: str = os.getenv("SERVER_ADDRESS") or ""  #http://icoservices.kube.isc.heia-fr.ch/


# *****************************************************************************
#                  FastAPI entry point declaration
# *****************************************************************************

rootapp = FastAPI()

app = FastAPI(openapi_url='/specification')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=NAME,
        version=VERSION,
        description=DESCRIPTION,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


rootapp.openapi = custom_openapi
rootapp.mount(URL_PREFIX, app)


# *****************************************************************************
#                  Set the logging for the service
# *****************************************************************************


logger = logging.getLogger("uvicorn.error")
logger.info('Starting app with URL_PREFIX=' + URL_PREFIX)


# ******************************************************************************
#             Classes declaration - for input and output models
# ******************************************************************************


class parameters(BaseModel):
    res: str
    budget: int
    perf: int


# *****************************************************************************
#                  Done once when micro-service is starting up
# *****************************************************************************


@rootapp.on_event("startup")
def initialization():
    global case, mb, rad, power, merged_cpu, merged_gpu, merged_ssd, merged_ram
    ram = pd.read_csv("data/ram.csv")
    ssd = pd.read_csv("data/ssd.csv")
    ssd_ = pd.read_csv("data/ssd_.csv")
    ram2 = pd.read_csv("data/ram2.csv")
    cpu = pd.read_csv("data/cpu.csv")
    gpu = pd.read_csv("data/gpu.csv")
    cpu2 = pd.read_csv("data/cpu2.csv")
    gpu2 = pd.read_csv("data/gpu2.csv")
    case = pd.read_csv("data/case.csv")
    power = pd.read_csv("data/power.csv")
    mb = pd.read_csv("data/mb.csv")
    rad = pd.read_csv("data/rad.csv")
    
    # Looking for the closest match for all element inside both dataframes by applying the fuzzy function, then merging on the closest_match.
    cpu['closest_match'] = cpu['Model'].apply(lambda x: find_closest_match(x, cpu2['name']))
    cpu2['closest_match'] = cpu2['name'].apply(lambda x: find_closest_match(x, cpu['Model']))
    merged_cpu = pd.merge(cpu, cpu2, left_on='Model', right_on='closest_match')
    merged_cpu['keep'] = merged_cpu.apply(lambda row: 1 if row['closest_match_y'] in row['name'] else 0, axis=1)
    merged_cpu = merged_cpu[merged_cpu["keep"]==1].sort_values("Benchmark", ascending=False).drop(['name', 'Type', 'closest_match_x','closest_match_y','keep','URL','Samples'], axis=1)
    merged_cpu['price'] = merged_cpu['price'].str.replace("'", "").astype(int)

    # Looking for the closest match for all element inside both dataframes by applying the fuzzy function, then merging on the closest_match.
    gpu['closest_match'] = gpu['Part Number'].apply(lambda x: find_closest_match(x, gpu2['model']))
    gpu2['closest_match'] = gpu2['model'].apply(lambda x: find_closest_match(x, gpu['Part Number']))
    merged_gpu = pd.merge(gpu, gpu2, left_on='Part Number', right_on='closest_match')
    merged_gpu['keep'] = merged_gpu.apply(lambda row: 1 if row['closest_match_x'] in row['model'] else 0, axis=1)
    merged_gpu = merged_gpu[merged_gpu["keep"]==1].sort_values("Benchmark", ascending=False).drop(['Part Number', 'name', 'closest_match_y', 'closest_match_x', 'Brand', "keep", 'Type','URL','Samples'], axis=1)
    
    merged_ssd = pd.merge(ssd, ssd_, on='Model')
    merged_ram = pd.merge(ram, ram2, on='Model')
    
    power['power'] = clean(power['power'], "W", "", float)
    merged_gpu['power_usage'] = clean(merged_gpu['power_usage'], "W", "", float)
    merged_gpu['price'] = clean(merged_gpu['price'], "'", "", float)
    merged_gpu['length'] = clean(merged_gpu['length'], "mm", "", float)
    case["len_gpu_max"] = clean(case["len_gpu_max"], "mm", "", float)
    rad["largeur"] = clean(rad["largeur"], "mm", "", float)
    

# ******************************************************************************
#                  API Route definition
# ******************************************************************************


@app.get("/")
def info():
    return {'message': 'Welcome to CyberCraft, your very own personal computer configurator. Try out /showcase for the showcase and /docs for the doc.'}


@app.post("/build")
async def build(params: parameters):
    global budget, ram, gpu, cpu, ssd, mb, rad, power, case
    initialization()
    if params: logger.info('User requirements received')
    else: raise logger.error("Failed to import the user's requirements")
    budget = params.budget
    gpu = unit(merged_gpu[merged_gpu['price'] < budget*0.3]).iloc[[0]]
    cpu = unit(merged_cpu[merged_cpu['price'] < budget*0.2]).iloc[[0]]
    ssd = unit(merged_ssd[merged_ssd['price'] < budget*0.1]).iloc[[0]]
    ram = unit(merged_ram[merged_ram['price'] < budget*0.1]).iloc[[0]]
    mb = listing(mb, budget, 0.1)
    power = listing(power, budget, 0.1)
    rad = listing(rad, budget, 0.1)
    case = listing(case, budget, 0.03)
    mb, power, rad, case = compatibility()
    # Scrapping the top priced supplier URLs
    arg = [gpu.at[0,'Model'], cpu.at[0,'Model'], ssd.at[0,'Model'], ram.at[0,'Model'], mb, power, rad, case]
    scrapp_latest_prices(arg)
    config = pd.read_csv('config.csv')
    config['name'] = config['name'].str[:25]
    #config['closest_match'] = config['name'].apply(lambda x: find_closest_match(x, arg))
    config = config.drop(['url'], axis=1)  #'name'
    config['type'] = config['type'].str.replace("Cartes graphiques & accessoires", "Carte graphique").replace("Processeurs", "Processeur")\
        .replace("Disques durs & SSD", "Disque dur & SSD").replace("Refroidissement par eau", "Refroidissement").replace("Cartes mères", "Carte mère")\
            .replace("Boîtiers & alimentation", "Boîtier & alimentation")  
    return {'component1': config.iloc[[0]].to_json(orient='records'), 'component2': config.iloc[[1]].to_json(orient='records'), 
            'component3': config.iloc[[2]].to_json(orient='records'), 'component4': config.iloc[[3]].to_json(orient='records'),
            'component5': config.iloc[[4]].to_json(orient='records'), 'component6': config.iloc[[5]].to_json(orient='records'), 
            'component7': config.iloc[[6]].to_json(orient='records'), 'component8': config.iloc[[7]].to_json(orient='records')}

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
    process.crawl(QuotesSpider)
    process.start()
    process.stop()

def clean(df, carac1, carac2, type):
    return df.str.replace(carac1, carac2).astype(type)
    
# define a function to find the closest match between two strings
def find_closest_match(x, choices):
    return max(choices, key=lambda y: fuzz.ratio(x, y) if x and y else "No match found")

def partial_ratio_1(x, y):
    return fuzz.partial_ratio(x, y, score_cutoff=1)

# define a function to find the best match
def unit(df):
    return df[df['Benchmark'] == df['Benchmark'].max()].sort_values(by="price").iloc[[0]].reset_index(drop=True)

def listing(df, budget, factor):
    return df[df['price'] < budget*factor].sort_values(by="price", ascending=False).reset_index(drop=True)

# define a function to check the compatibility between pairs of hardwares and returns the selected component
def compatibility():
    global case, mb, rad, power
    choice_case = 0
    choice_mb = 0
    choice_power = 0
    choice_rad = 0
    
    # Selecting motherboard with budget and memory type as constraints
    while mb.at[choice_mb,"memory_type"] not in ram.at[0,"Model"] or mb.at[choice_mb,"price"] > budget * 0.1:
        choice_mb +=1
    
    # Selecting power supply with budget and gpu power usage as constraints
    while power.at[choice_power,"power"] <  gpu.at[0,"power_usage"] or power.at[choice_power,"price"] > budget * 0.1:
        choice_power +=1
    
    # Selecting cooling system with budget as constraint
    rad = rad.iloc[[choice_case]]
    
    # Selecting case with budget, gpu length, rad length and motherboard type as constraints
    while case.at[choice_case,"len_gpu_max"] <  rad.at[choice_rad,"largeur"] or case.at[choice_case,"len_gpu_max"] < gpu.at[0,"length"]  \
        or (mb.at[choice_mb,"format"] != case.at[choice_case,"type_mb1"] and mb.at[choice_mb,"format"] != case.at[choice_case,"type_mb2"]):
        choice_case += 1   
    
    return  mb.at[choice_power,"name"], \
            power.at[choice_power,"name"], \
            rad.at[choice_power,"name"], \
            case.at[choice_power,"name"], 
    