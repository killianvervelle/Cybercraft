import pandas as pd

class Optimizer:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path = "data/clean/merged/"
        self.cpu = pd.read_csv(path + "CPU.csv", encoding='latin-1')
        self.gpu = pd.read_csv(path + "GPU.csv", encoding='latin-1')
        self.ram = pd.read_csv(path + "RAM.csv", encoding='latin-1')
        self.ssd = pd.read_csv(path + "SSD.csv", encoding='latin-1')
        
        
    def optimize(self):
        '''
        Pick the best element from each list
        '''
        # Look for an appropried optimization algorithm, like branch-and-bound for instance.
        # Dynamic programming looks promising too.
        pass