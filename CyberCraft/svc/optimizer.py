import pandas as pd
import numpy as np

class Optimizer:
    
    def __init__(self, max_budget:float):
        '''
        Load the data from the CSV
        '''
        self.max_budget = max_budget
        
    def from_filename(self):
        path = "data/clean/merged/"
        self.cpu = pd.read_csv(path + "CPU.csv", encoding='latin-1')
        self.gpu = pd.read_csv(path + "GPU.csv", encoding='latin-1')
        self.ram = pd.read_csv(path + "RAM.csv", encoding='latin-1')
        self.ssd = pd.read_csv(path + "SSD.csv", encoding='latin-1')
        
    def from_dataframes(self, cpu:pd.DataFrame, gpu:pd.DataFrame, ram:pd.DataFrame, ssd:pd.DataFrame):
        self.cpu = cpu
        self.gpu = gpu
        self.ram = ram
        self.ssd = ssd
        
    def preprocess(self):
        '''
        Prepare the data for the optimizer
        '''
        self.ram["benchmark"] = self.ram["benchmark"] * self.ram["memory"].apply(np.log)
        self.ssd["benchmark"] = self.ssd["benchmark"] * self.ssd["memory"].apply(np.log)
        self.cpu = self.filter_sort_scale(self.cpu)
        self.gpu = self.filter_sort_scale(self.gpu)
        self.ram = self.filter_sort_scale(self.ram)
        self.ssd = self.filter_sort_scale(self.ssd)
    
    def filter_sort_scale(self, df:pd.DataFrame):
        '''
        Filter the interesting columns, sort and normalize them
        '''
        df[['benchmark', 'price']] = df[['benchmark', 'price']].apply(pd.to_numeric)
        df['benchmark'] = self.normalize_column(df['benchmark'])
        df = df.sort_values(by=['benchmark', 'price'], ascending=False)
        return df
        
    def normalize_column(self, column:pd.Series):
        '''
        Normalize the given column from 0 to 1
        '''
        return (column-column.min())/(column.max()-column.min())
    
    def filter_expensive(self):
        '''
        Filter prices higher than the threshold for every category
        '''
        self.cpu = self.filter_prices(self.cpu, self.cpu["price"].iloc[0])
        self.gpu = self.filter_prices(self.gpu, self.gpu["price"].iloc[0])
        self.ram = self.filter_prices(self.ram, self.ram["price"].iloc[0])
        self.ssd = self.filter_prices(self.ssd, self.ssd["price"].iloc[0])
    
    def filter_prices(self, df:pd.DataFrame, price:float):
        '''
        Filter prices higher than the threshold
        '''
        cols = ["price"]
        df[cols] = df[df[cols] <= price][cols]
        df = df.dropna()
        return df
    
    def select_next_componant(self):
        '''
        Select the next most powerful component
        '''
        # First, identify which component is the next directly less powerful
        next_cpu = self.cpu["benchmark"].iloc[1] if self.cpu.shape[0] > 1 else 0
        next_gpu = self.gpu["benchmark"].iloc[1] if self.gpu.shape[0] > 1 else 0
        next_ram = self.ram["benchmark"].iloc[1] if self.ram.shape[0] > 1 else 0
        next_ssd = self.ssd["benchmark"].iloc[1] if self.ssd.shape[0] > 1 else 0
        max_val = np.argmax((next_cpu, next_gpu, next_ram, next_ssd))
        
        # Then, pick the next most powerful component
        if max_val == 0:
            self.cpu = self.cpu.iloc[1:]
        elif max_val == 1:
            self.gpu = self.gpu.iloc[1:]
        elif max_val == 2:
            self.ram = self.ram.iloc[1:]
        elif max_val == 3:
            self.ssd = self.ssd.iloc[1:]
        
    def print_results(self):
        '''
        Print the selected components
        '''
        print(f"selected CPU : {self.cpu['model'].iloc[0]}, with performance {self.cpu['benchmark'].iloc[0]:.3f} and price {self.cpu['price'].iloc[0]:.2f} CHF.")
        print(f"selected GPU : {self.gpu['model'].iloc[0]}, with performance {self.gpu['benchmark'].iloc[0]:.3f} and price {self.gpu['price'].iloc[0]:.2f} CHF.")
        print(f"selected RAM : {self.ram['model'].iloc[0]}, with performance {self.ram['benchmark'].iloc[0]:.3f} and price {self.ram['price'].iloc[0]:.2f} CHF.")
        print(f"selected SSD : {self.ssd['model'].iloc[0]} {self.ssd['memory'].iloc[0]}GB, with performance {self.ssd['benchmark'].iloc[0]:.3f} and price {self.ssd['price'].iloc[0]:.2f} CHF.")
        print(f"With a final budget of {self.current_budget:.2f} CHF. Maximum budget was {self.max_budget:.2f} CHF.")
    
    def branch_and_bound(self):
        '''
        Pick the best componants of each category using a branch and bound optimization algorithm.
        '''
        # First, check that the budget allows a configuration with each cheapest element
        min_budget = self.cpu["price"].min() + self.gpu["price"].min() + \
            self.ram["price"].min() + self.ssd["price"].min()
        if min_budget > self.max_budget:
            return None
        
        # Then, start by picking the most performant element of each category
        self.current_budget = self.cpu["price"].iloc[0] + self.gpu["price"].iloc[0] + \
            self.ram["price"].iloc[0] + self.ssd["price"].iloc[0]
            
        while self.current_budget > self.max_budget:
            # Filters out all components that cost more than the current ones
            self.filter_expensive()
            
            # Select the next directly less powerful component
            self.select_next_componant()
            
            self.current_budget = self.cpu["price"].iloc[0] + self.gpu["price"].iloc[0] + \
                self.ram["price"].iloc[0] + self.ssd["price"].iloc[0]
        
        return True
            
    def optimize(self):
        '''
        Run the optimizer
        '''
        self.preprocess()
        if self.branch_and_bound():
            self.print_results()
            return self.cpu, self.gpu, self.ram, self.ssd
        else:
            print(f"No configuration was possible with the given budget of {self.max_budget:.2f} CHF.")
            
            return None, None, None, None
        
def main():
    max_budget = 1500
    optimizer = Optimizer(max_budget)
    optimizer.from_filename()
    optimizer.optimize()
    
if __name__ == "__main__":
    main()