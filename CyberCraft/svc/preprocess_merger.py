import pandas as pd

class Merger:
    
    def __init__(self):
        '''
        Load the data from the CSV
        '''
        path_ldlc = "data/clean/LDLC/"
        self.cpu_ldlc = pd.read_csv(path_ldlc + "CPU.csv", encoding='latin-1')
        self.gpu_ldlc = pd.read_csv(path_ldlc + "GPU.csv", encoding='latin-1')
        # self.hdd_ldlc = pd.read_csv(path_ldlc + "HDD.csv", encoding='latin-1')
        self.ram_ldlc = pd.read_csv(path_ldlc + "RAM.csv", encoding='latin-1')
        self.ssd_ldlc = pd.read_csv(path_ldlc + "SSD.csv", encoding='latin-1')
        
        path_usr_bench = "data/clean/UserBenchmarks/"
        self.cpu_usr = pd.read_csv(path_usr_bench + "CPU.csv", encoding='latin-1')
        self.gpu_usr = pd.read_csv(path_usr_bench + "GPU.csv", encoding='latin-1')
        # self.hdd_usr = pd.read_csv(path_usr_bench + "HDD.csv", encoding='latin-1')
        self.ram_usr = pd.read_csv(path_usr_bench + "RAM.csv", encoding='latin-1')
        self.ssd_usr = pd.read_csv(path_usr_bench + "SSD.csv", encoding='latin-1')
        
    def normalize_column(self, column:pd.Series):
        return (column-column.min())/(column.max()-column.min())
    
    def merge_cpu(self):
        '''
        Merge the cpu by the model and the brand
        '''
        # Merge the cpu files together
        self.cpu = pd.merge(self.cpu_ldlc, self.cpu_usr, how='outer', on=['model', 'brand'])
        
        # Remove rows with missing values
        self.cpu = self.cpu.dropna()
        
        self.cpu['value'] = self.cpu['benchmark'] / self.cpu['price']
        self.cpu['value'] = self.normalize_column(self.cpu['value'])
        self.cpu['value'] = self.cpu['value'].round(3)
        

    def merge_gpu(self):
        '''
        Merge the gpu by the model and the brand
        '''
        # Merge the gpu files together
        self.gpu = pd.merge(self.gpu_ldlc, self.gpu_usr, how='outer', on=['model', 'brand'])
        
        # Remove rows with missing values
        self.gpu = self.gpu.dropna()
        
        self.gpu['value'] = self.gpu['benchmark'] / self.gpu['price']
        self.gpu['value'] = self.normalize_column(self.gpu['value'])
        self.gpu['value'] = self.gpu['value'].round(3)

    def merge_ssd(self):
        '''
        Merge the ssd by the model, the brand and the memory
        '''
        # Merge the gpu files together
        self.ssd_ldlc['brand'] = self.ssd_ldlc['brand'].str.lower().str.strip()
        self.ssd_ldlc['model'] = self.ssd_ldlc['model'].str.lower().str.strip()
        self.ssd_usr['brand'] = self.ssd_usr['brand'].str.lower().str.strip()
        self.ssd_usr['model'] = self.ssd_usr['model'].str.lower().str.strip()
        self.ssd = pd.merge(self.ssd_ldlc, self.ssd_usr, how='outer', on=['model', 'brand', 'memory'])
        
        # Remove rows with missing values
        self.ssd = self.ssd.dropna()
        
        self.ssd['value'] = self.ssd['benchmark'] / self.ssd['price'] * self.ssd['memory']
        self.ssd['value'] = self.normalize_column(self.ssd['value'])
        self.ssd['value'] = self.ssd['value'].round(3)
        
        
    def merge_ram(self):
        '''
        Merge the ram by the model and the brand
        '''
        # Merge the gpu files together
        # self.ram_ldlc['brand'] = self.ram_ldlc['brand'].str.lower().str.strip()
        # self.ram_ldlc['model'] = self.ram_ldlc['model'].str.lower().str.strip()
        # self.ram_usr['brand'] = self.ram_usr['brand'].str.lower().str.strip()
        # self.ram_usr['model'] = self.ram_usr['model'].str.lower().str.strip()
        self.ram_ldlc['part number'] = self.ram_ldlc['part number'].str.lower().str.strip()
        self.ram_usr['part number'] = self.ram_usr['part number'].str.lower().str.strip()
        self.ram = pd.merge(self.ram_ldlc, self.ram_usr, how='outer', on=['part number'])
        
        # Remove rows with missing values
        self.ram = self.ram.dropna()
        
        self.ram['value'] = self.ram['benchmark'] / self.ram['price'] * self.ram['memory']
        self.ram['value'] = self.normalize_column(self.ram['value'])
        self.ram['value'] = self.ram['value'].round(3)
        
    def save_csv(self):
        '''
        Save the cleaned CSV
        '''
        path = "data/clean/merged/"
        self.cpu.to_csv(path + "CPU.csv", sep=',', encoding='utf-8', index=False)
        self.gpu.to_csv(path + "GPU.csv", sep=',', encoding='utf-8', index=False)
        # self.hdd.to_csv(path + "HDD.csv", sep=',', encoding='utf-8', index=False)
        self.ram.to_csv(path + "RAM.csv", sep=',', encoding='utf-8', index=False)
        self.ssd.to_csv(path + "SSD.csv", sep=',', encoding='utf-8', index=False)
        
        
        
def main():
    preProcess = Merger()
    preProcess.merge_cpu()
    preProcess.merge_gpu()
    # preProcess.merge_hdd()
    preProcess.merge_ram()
    preProcess.merge_ssd()
    preProcess.save_csv()
    
if __name__ == "__main__":
    main()