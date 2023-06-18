import re
import pandas as pd

class PreProcess:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path = "../data/raw/UserBenchmarks/"
        self.cpu = pd.read_csv(path + "CPU_UserBenchmarks.csv")
        self.gpu = pd.read_csv(path + "GPU_UserBenchmarks.csv")
        self.hdd = pd.read_csv(path + "HDD_UserBenchmarks.csv")
        self.ram = pd.read_csv(path + "RAM_UserBenchmarks.csv")
        self.ssd = pd.read_csv(path + "SSD_UserBenchmarks.csv")
        
        # Put the columns name to lowercase
        self.cpu.columns = map(str.lower, self.cpu.columns)
        self.gpu.columns = map(str.lower, self.gpu.columns)
        self.hdd.columns = map(str.lower, self.hdd.columns)
        self.ram.columns = map(str.lower, self.ram.columns)
        self.ssd.columns = map(str.lower, self.ssd.columns)
        
    def filter_cpu(self):
        '''
        Filter the cpu to only keep the unique models
        '''
        self.cpu = self.cpu.drop('part number', axis=1)
    
    def filter_gpu(self):
        '''
        Filter the gpu to only keep the unique models
        '''
        # Only keep the AMD and NVIDIA brands
        self.gpu = self.gpu[self.gpu['brand'].str.contains('AMD|Nvidia')]
        
        # Remove row that have a part number
        self.gpu = self.gpu[self.gpu['part number'].isnull()]
        self.gpu = self.gpu.drop('part number', axis=1)
        
        # Remove models where we have certains keywords that we don't want (like MOBILE of LAPTOP)
        self.gpu = self.gpu[~self.gpu["model"].str.contains('Mobile|Laptop|Quadro|GeForce|Radeon HD|FirePro|iGPU')]
        
        # process the data once filtered
        self.gpu['model'] = self.gpu['model'].str.replace('-', ' ')
        self.gpu['brand'] = self.gpu['brand'].str.upper()
        
    def filter_ram(self):
        '''
        Filter the ram
        '''        
        # Remove the old DDR3 standard
        self.ram = self.ram[~self.ram['model'].str.contains('DDR3')]
        
        # Get the number of sticks and the memory of each one
        self.ram[['number of sticks', 'memory of each stick']] = self.ram['model'].str.extract(r'(\d+)x(\d+)GB').astype(int)
        
        # Add a column with the total memory
        self.ram['memory'] = self.ram['number of sticks'] * self.ram['memory of each stick']
        
    def get_memory(self, cell:str, re_memory:str, tb_to_gb:int=1000):
        match = re.search(re_memory, cell)
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if unit == 'T':
                value *= tb_to_gb
            return value
        else:
            return None
    
    def filter_hdd(self):
        '''
        Filter the hdd
        '''
        # Extract the HDD memory
        re_memory = r'\s*(\d+)\s*(T|G)B.*'
        self.hdd['memory'] = self.hdd.apply(lambda row: self.get_memory(row['model'], re_memory=re_memory, tb_to_gb=1024), axis=1)
        self.hdd['model'] = self.hdd['model'].str.replace(f'(?i){re_memory}', '', regex=True)

    def filter_ssd(self):
        '''
        Filter the ssd
        '''        
        # Remove other terms from the designation column
        terms_to_remove = ['SSD', 'M.2', 'PCIe', 'NVMe', '2280', 'NAND', '3D', 'WD']
        for term in terms_to_remove:
            self.ssd['model'] = self.ssd['model'].str.replace(f'(?i){term}', '', regex=True)
        
        # Extract the SSD memory
        re_memory = r'\s*(\d+)\s*(T|G)B.*'
        self.ssd['memory'] = self.ssd.apply(lambda row: self.get_memory(row['model'], re_memory=re_memory, tb_to_gb=1024), axis=1)
        self.ssd['model'] = self.ssd['model'].str.replace(f'(?i){re_memory}', '', regex=True)
        
        self.ssd = self.ssd.drop('part number', axis=1)
        
        
    def remove_unused_columns(self):
        '''
        Remove columns that are not useful for optimization
        '''
        columns_to_remove = ['type', 'rank', 'samples', 'url']
        self.cpu = self.cpu.drop(columns_to_remove, axis=1)
        self.gpu = self.gpu.drop(columns_to_remove, axis=1)
        self.hdd = self.hdd.drop(columns_to_remove, axis=1)
        self.ram = self.ram.drop(columns_to_remove, axis=1)
        self.ssd = self.ssd.drop(columns_to_remove, axis=1)
        
    def save_csv(self):
        '''
        Save the cleaned CSV
        '''
        path = "../data/clean/UserBenchmarks/"
        self.cpu.to_csv(path + "CPU.csv", sep=',', encoding='utf-8', index=False)
        self.gpu.to_csv(path + "GPU.csv", sep=',', encoding='utf-8', index=False)
        self.hdd.to_csv(path + "HDD.csv", sep=',', encoding='utf-8', index=False)
        self.ram.to_csv(path + "RAM.csv", sep=',', encoding='utf-8', index=False)
        self.ssd.to_csv(path + "SSD.csv", sep=',', encoding='utf-8', index=False)
        
        
        
def main():
    preProcess = PreProcess()
    preProcess.remove_unused_columns()
    preProcess.filter_cpu()
    preProcess.filter_gpu()
    preProcess.filter_hdd()
    preProcess.filter_ram()
    preProcess.filter_ssd()
    preProcess.save_csv()
    
if __name__ == "__main__":
    main()