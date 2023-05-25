import re
import pandas as pd

class PreProcess:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path = "data/raw/LDLC/"
        self.cpu = pd.read_csv(path + "CPU.csv", encoding='latin-1')
        self.gpu = pd.read_csv(path + "GPU.csv", encoding='latin-1')
        self.hdd = pd.read_csv(path + "HDD.csv", encoding='latin-1')
        self.ram = pd.read_csv(path + "RAM.csv", encoding='latin-1')
        self.ssd = pd.read_csv(path + "SSD.csv", encoding='latin-1')
        self.psu = pd.read_csv(path + "PSU.csv", encoding='latin-1')
        self.case = pd.read_csv(path + "case.csv", encoding='latin-1')
        self.ventirad = pd.read_csv(path + "ventirad.csv", encoding='latin-1')
        self.motherboard = pd.read_csv(path + "motherboard.csv", encoding='latin-1')
        
    def filter_cpu(self):
        '''
        Get the CPU brand, model and socket
        '''
        # Get the brand of the cpu
        re_brand = r'^(\w+)\b'
        self.cpu['Brand'] = self.cpu['designation'].str.extract(re_brand)

        # Get the model of the cpu
        re_core = r'\b(Core\s+i\d-\d+[a-zA-Z]*)\b'
        re_ryzen = r'\b(Ryzen\s+[0-9]\s+\w*\s*\d+\w*)\b'
        self.cpu['Model'] = self.cpu['designation'].str.extract(re_core).combine_first(self.cpu['designation'].str.extract(re_ryzen))

        # Get the socket of the cpu
        re_socket = r'\b[sS]ocket\s+(\w+)\b'
        self.cpu['Socket'] = self.cpu['description'].str.extract(re_socket)
        

    def filter_gpu(self):
        '''
        Filter the gpu to only keep the unique models
        '''

        # Get the brand of the gpu
        re_brand = r'(NVIDIA|AMD){1}'
        self.gpu['Brand'] = self.gpu['description'].str.extract(re_brand)

        # Get the model of the gpu
        re_model_nvidia = r'\b([GR]TX*\s+\d+\s*T*i*)\b'
        re_model_amd = r'\b(RX\s+\d+\s*X*T*X*)\b'
        self.gpu['Model'] = self.gpu['description'].str.extract(re_model_nvidia) \
             .combine_first(self.gpu['description'].str.extract(re_model_amd))

        # Get the memory of the gpu
        re_memory = r'^(\d+)\s*Go\b'
        self.gpu['Memory'] = self.gpu['description'].str.extract(re_memory)

        # Group the same model and averages the prices
        self.gpu = self.gpu.groupby(['Brand', 'Model', 'Memory'], axis=0, as_index=False).mean(['price']).round(2)
        
    def filter_ram(self):
        '''
        Filter the ram
        '''
        # Get the part number from the ram
        re_part_number = r'\s+-\s+\b([A-Z0-9\/\-]{10,})'
        self.ram['Part Number'] = self.ram['description'].str.extract(re_part_number)
    
    def filter_hdd(self):
        '''
        Filter the hdd
        '''
        self.hdd['Memory'] = self.hdd['Model'].apply(self.get_memory)

    def filter_ssd(self):
        '''
        Filter the ssd
        '''
        brands = ['Samsung', 'Crucial', 'Kingston', 'Western Digital', 'Fox Spirit', 'Seagate', 'Textorm', 'Intel', 'Corsair']
        
        self.ssd['Memory'] = self.ssd.apply(lambda row: self.get_memory(row['Model'], tb_to_gb=1024), axis=1)
        
        
    def remove_unused_columns(self):
        '''
        Remove columns that are not useful for optimization
        '''
        columns_to_remove = ['designation', 'description']
        self.cpu = self.cpu.drop(columns_to_remove, axis=1)
        # self.gpu = self.gpu.drop(columns_to_remove, axis=1)
        self.hdd = self.hdd.drop(columns_to_remove, axis=1)
        self.ram = self.ram.drop(columns_to_remove, axis=1)
        self.ssd = self.ssd.drop(columns_to_remove, axis=1)
        
    def save_csv(self):
        '''
        Save the cleaned CSV
        '''
        path = "data/clean/LDLC/"
        self.cpu.to_csv(path + "CPU.csv", sep=',', encoding='utf-8', index=False)
        self.gpu.to_csv(path + "GPU.csv", sep=',', encoding='utf-8', index=False)
        # self.hdd.to_csv(path + "HDD.csv", sep=',', encoding='utf-8', index=False)
        self.ram.to_csv(path + "RAM.csv", sep=',', encoding='utf-8', index=False)
        # self.ssd.to_csv(path + "SSD.csv", sep=',', encoding='utf-8', index=False)
        
        
        
def main():
    preProcess = PreProcess()
    preProcess.filter_cpu()
    preProcess.filter_gpu()
    # preProcess.filter_hdd()
    preProcess.filter_ram()
    # preProcess.filter_ssd()
    preProcess.remove_unused_columns()
    preProcess.save_csv()
    
if __name__ == "__main__":
    main()