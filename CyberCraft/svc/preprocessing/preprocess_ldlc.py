import re
import pandas as pd

class PreProcess:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path = "../data/raw/LDLC/"
        self.cpu = pd.read_csv(path + "CPU.csv", encoding='latin-1')
        self.gpu = pd.read_csv(path + "GPU.csv", encoding='latin-1')
        self.gpu_specs = pd.read_csv(path + "GPU_specs.csv", encoding='latin-1')
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
        self.cpu['brand'] = self.cpu['designation'].str.extract(re_brand)

        # Get the model of the cpu
        re_core = r'\b(Core\s+i\d-\d+[a-zA-Z]*)\b'
        re_ryzen = r'\b(Ryzen\s+[0-9]\s+\w*\s*\d+\w*)\b'
        self.cpu['model'] = self.cpu['designation'].str.extract(re_core).combine_first(self.cpu['designation'].str.extract(re_ryzen))

        # Get the socket of the cpu
        re_socket = r'\b[sS]ocket\s+(\w+)\b'
        self.cpu['socket'] = self.cpu['description'].str.extract(re_socket)
        

    def filter_gpu(self):
        '''
        Filter the gpu to only keep the unique models
        '''

        # Get the brand of the gpu
        re_brand = r'(NVIDIA|AMD){1}'
        self.gpu['brand'] = self.gpu['description'].str.extract(re_brand)

        # Get the model of the gpu
        re_model_nvidia = r'\b([GR]TX*\s+\d+\s*T*i*)\b'
        re_model_amd = r'\b(RX\s+\d+\s*X*T*X*)\b'
        self.gpu['model'] = self.gpu['description'].str.extract(re_model_nvidia) \
             .combine_first(self.gpu['description'].str.extract(re_model_amd))

        # Get the memory of the gpu
        re_memory = r'^(\d+)\s*Go\b'
        self.gpu['memory'] = self.gpu['description'].str.extract(re_memory)

        # Group the same model and averages the prices
        self.gpu = self.gpu.groupby(['brand', 'model', 'memory'], axis=0, as_index=False).mean(['price']).round(2)
        
    def filter_gpu_specs(self):
        '''
        Add lenght and power data to the gpu specs
        '''

        # Get the model of the gpu
        re_model_nvidia = r'\b([GR]TX*\s+\d+\s*T*i*)\b'
        re_model_amd = r'\b(RX\s+\d+\s*X*T*X*)\b'
        self.gpu_specs['model'] = self.gpu_specs['name'].str.extract(re_model_nvidia) \
             .combine_first(self.gpu_specs['name'].str.extract(re_model_amd))
             
        
        self.gpu_specs['power_usage'] = self.gpu_specs['power_usage'].str.replace('W', '').astype('int')
        self.gpu_specs['length'] = self.gpu_specs['length'].str.replace('mm', '').astype('float')

        # Group the same model and averages the prices
        self.gpu_specs = self.gpu_specs.groupby(['model'], axis=0, as_index=False).max(['power_usage', 'length']).round(1)
        
        # Add the specs to the gpu models
        self.gpu_specs['model'] = self.gpu_specs['model'].str.strip()
        self.gpu = pd.merge(self.gpu, self.gpu_specs, how='outer', on=['model'])
        
        # Remove rows with missing values
        self.gpu = self.gpu.dropna()
        
    def filter_ram(self):
        '''
        Filter the ram
        '''
        # Get the part number from the ram
        re_part_number = r'\s+-\s+\b([A-Z0-9\/\-]{10,})'
        self.ram['part number'] = self.ram['description'].str.extract(re_part_number)
        
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
        self.hdd['memory'] = self.hdd['model'].apply(self.get_memory)
        
    # Function to extract brand names from designation
    def extract_brand_name(self, row, brands_names):
        for brand in brands_names:
            if brand in row['designation']:
                return brand
        return None

    def filter_ssd(self):
        '''
        Filter the ssd
        '''
        # Extract the SSD brands
        brands_names = ['Samsung', 'Crucial', 'Kingston', 'Western Digital', 'Fox Spirit', 'Seagate', 'Textorm', 'Intel', 'Corsair', 'LDLC']
        
        # Extract brand names and create a new column
        self.ssd['brand'] = self.ssd.apply(lambda x: self.extract_brand_name(x, brands_names), axis=1)
        self.ssd['brand'] = self.ssd['brand'].str.replace('Western Digital', 'WD')

        # Remove brand names from the designation column
        for brand in brands_names:
            self.ssd['designation'] = self.ssd['designation'].str.replace(brand, '')
        
        # Remove other terms from the designation column
        terms_to_remove = ['SSD', 'M.2', 'PCIe', 'NVMe', '2280', 'NAND', '3D', 'WD']
        for term in terms_to_remove:
            self.ssd['designation'] = self.ssd['designation'].str.replace(f'(?i){term}', '', regex=True)
        
        # Extract the SSD memory
        re_memory = r'\s*(\d+)\s*(T|G)[Bo].*'
        self.ssd['memory'] = self.ssd.apply(lambda row: self.get_memory(row['designation'], re_memory=re_memory, tb_to_gb=1024), axis=1)
        self.ssd['designation'] = self.ssd['designation'].str.replace(f'(?i){re_memory}', '', regex=True)
        
        # Remove the '_' symbol
        self.ssd['designation'] = self.ssd['designation'].str.replace('_', '')
        
        # Put the filtered designation in the Model column
        self.ssd['model'] = self.ssd['designation']
                
        
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
        path = "../data/clean/LDLC/"
        self.cpu.to_csv(path + "CPU.csv", sep=',', encoding='utf-8', index=False)
        self.gpu.to_csv(path + "GPU.csv", sep=',', encoding='utf-8', index=False)
        # self.hdd.to_csv(path + "HDD.csv", sep=',', encoding='utf-8', index=False)
        self.ram.to_csv(path + "RAM.csv", sep=',', encoding='utf-8', index=False)
        self.ssd.to_csv(path + "SSD.csv", sep=',', encoding='utf-8', index=False)
        
        
        
def main():
    preProcess = PreProcess()
    preProcess.filter_cpu()
    preProcess.filter_gpu()
    preProcess.filter_gpu_specs()
    # preProcess.filter_hdd()
    preProcess.filter_ram()
    preProcess.filter_ssd()
    preProcess.remove_unused_columns()
    preProcess.save_csv()
    
if __name__ == "__main__":
    main()