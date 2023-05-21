import re
import pandas as pd

class PreProcess:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path = "data/raw/UserBenchmarks/"
        self.cpu = pd.read_csv(path + "CPU_UserBenchmarks.csv")
        self.gpu = pd.read_csv(path + "GPU_UserBenchmarks.csv")
        self.hdd = pd.read_csv(path + "HDD_UserBenchmarks.csv")
        self.ram = pd.read_csv(path + "RAM_UserBenchmarks.csv")
        self.ssd = pd.read_csv(path + "SSD_UserBenchmarks.csv")
        
    def filter_gpu(self):
        '''
        Filter the gpu to only keep the unique models
        '''
        # Only keep the AMD and NVIDIA brands
        self.gpu = self.gpu[self.gpu['Brand'].str.contains('AMD|Nvidia')]
        
        # Remove row that have a part number
        self.gpu = self.gpu[self.gpu['Part Number'].isnull()]
        self.gpu = self.gpu.drop('Part Number', axis=1)
        
        # Remove models where we have certains keywords that we don't want (like MOBILE of LAPTOP)
        self.gpu = self.gpu[~self.gpu["Model"].str.contains('Mobile|Laptop|Quadro|GeForce|Radeon HD|FirePro|iGPU')]
        
        # Only keep models containing recent names
        # self.gpu = self.gpu[self.gpu['Model'].str.contains(['RX', 'RTX', 'Radeon', 'GTX', 'Titan'])]
        
        # Only keep 
        
    def filter_ram(self):
        '''
        Filter the ram
        '''
        # Remove the old DDR3 standard
        self.ram = self.ram[~self.ram['Model'].str.contains('DDR3')]
        
        # Get the number of sticks and the memory of each one
        self.ram[['Number of sticks', 'Capacity of each stick']] = self.ram['Model'].str.extract(r'(\d+)x(\d+)GB').astype(int)
        
        # Add a column with the total memory
        self.ram['Total capacity'] = self.ram['Number of sticks'] * self.ram['Capacity of each stick']
        
    def get_memory(self, cell:str, tb_to_gb:int=1000):
            match = re.search(r'(\d+)\s*(T|G)B', cell)
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
        self.hdd['Memory'] = self.hdd['Model'].apply(self.get_memory)

    def filter_ssd(self):
        '''
        Filter the ssd
        '''
        self.ssd['Memory'] = self.ssd.apply(lambda row: self.get_memory(row['Model'], tb_to_gb=1024), axis=1)
        
        
    def remove_unused_columns(self):
        '''
        Remove columns that are not useful for optimization
        '''
        columns_to_remove = ['Type', 'Rank', 'Samples', 'URL']
        self.cpu = self.cpu.drop(columns_to_remove, axis=1)
        self.gpu = self.gpu.drop(columns_to_remove, axis=1)
        self.hdd = self.hdd.drop(columns_to_remove, axis=1)
        self.ram = self.ram.drop(columns_to_remove, axis=1)
        self.ssd = self.ssd.drop(columns_to_remove, axis=1)
        
    def save_csv(self):
        '''
        Save the cleaned CSV
        '''
        path = "data/clean/Optimization/"
        self.cpu.to_csv(path + "CPU.csv", sep=',', encoding='utf-8', index=False)
        self.gpu.to_csv(path + "GPU.csv", sep=',', encoding='utf-8', index=False)
        self.hdd.to_csv(path + "HDD.csv", sep=',', encoding='utf-8', index=False)
        self.ram.to_csv(path + "RAM.csv", sep=',', encoding='utf-8', index=False)
        self.ssd.to_csv(path + "SSD.csv", sep=',', encoding='utf-8', index=False)
        
        
        
def main():
    preProcess = PreProcess()
    preProcess.remove_unused_columns()
    preProcess.filter_gpu()
    preProcess.filter_hdd()
    preProcess.filter_ram()
    preProcess.filter_ssd()
    preProcess.save_csv()
    
if __name__ == "__main__":
    main()