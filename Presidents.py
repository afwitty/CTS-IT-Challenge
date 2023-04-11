import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Reader:
    def __init__(self, filename):
        self.filename = filename

    def read_csv(self):
        try:
            df = pd.read_csv(self.filename)
            df = df.drop(df.tail(1).index)
            return df
        except FileNotFoundError:
            print("File not found. Please check the file path and try again.")

    def add_variables(self, df):
        df['BIRTH_DATE_FORMATTED'] = df['BIRTH DATE'].apply(lambda x: pd.to_datetime(x, format="%b %d, %Y").strftime('%B %d, %Y') if isinstance(x, str) and x.split()[0] not in ['June', 'July'] else x)
        df['DEATH_DATE_FORMATTED'] = df['DEATH DATE'].apply(lambda x: pd.to_datetime(x, format="%b %d, %Y").strftime('%B %d, %Y') if isinstance(x, str) and x.split()[0] not in ['June', 'July'] else x)
        return df

class Writer:
    def __init__(self, df):
        self.df = df

    def add_variables(self):
        self.df['YEAR_OF_BIRTH'] = pd.to_datetime(self.df['BIRTH_DATE_FORMATTED'], format="%B %d, %Y").dt.year
        self.df['LIVED_YEARS'] = (pd.to_datetime(self.df['DEATH_DATE_FORMATTED'], format="%B %d, %Y") - pd.to_datetime(self.df['BIRTH_DATE_FORMATTED'], format="%B %d, %Y")).dt.days / 365.25
        self.df['LIVED_MONTHS'] = (pd.to_datetime(self.df['DEATH_DATE_FORMATTED'], format="%B %d, %Y") - pd.to_datetime(self.df['BIRTH_DATE_FORMATTED'], format="%B %d, %Y")).dt.days / 30.4375
        self.df['LIVED_DAYS'] = (pd.to_datetime(self.df['DEATH_DATE_FORMATTED'], format="%B %d, %Y") - pd.to_datetime(self.df['BIRTH_DATE_FORMATTED'], format="%B %d, %Y")).dt.days

    def write_statistics(self):
        lived_days = self.df['LIVED_DAYS']
        mean = lived_days.mean()
        weighted_average = ((self.df['LIVED_DAYS'] * self.df['LIVED_YEARS']).sum()) / self.df['LIVED_YEARS'].sum()
        median = lived_days.median()
        mode = my_mode(lived_days) 
        max_val = lived_days.max()
        min_val = lived_days.min()
        std_dev = lived_days.std() 

        print(f"{'='*50}")
        print(f"{'Statistics for Lived Days':^50}")
        print(f"{'='*50}")
        print(f"Mean: {mean:,.0f}")
        print(f"Weighted Average: {weighted_average:,.0f}")
        print(f"Median: {median:,.0f}")
        # print(f"Mode: {mode:,.0f}")
        if isinstance(mode, list):
            print(f"Mode(s): {', '.join(str(m) for m in mode)}")
        else:
            print(f"Mode: {mode}")
        print(f"Max: {max_val:,.0f}")
        print(f"Min: {min_val:,.0f}")
        print(f"Standard Deviation: {std_dev:,.0f}")      

    def write_output(self):
        self.add_variables()

        # Filter out living presidents
        self.df = self.df.dropna(subset=['DEATH DATE'])
        pd.options.display.float_format = '{:,.0f}'.format

        print(f"{'='*50}")
        print(f"{'Table of Top 10 Presidents':^50}")
        print(f"{'='*50}")

        # Get top 10 presidents who lived the longest
        longest_lived = self.df.nlargest(10, 'LIVED_YEARS')
        print("Top 10 Presidents from longest lived to shortest lived:")
        print(longest_lived[['PRESIDENT', 'YEAR_OF_BIRTH', 'LIVED_YEARS', 'LIVED_MONTHS', 'LIVED_DAYS']])

        # Get bottom 10 presidents who lived the shortest
        shortest_lived = self.df.nsmallest(10, 'LIVED_YEARS')
        print("Top 10 presidents from shortest lived to longest lived:")
        print(shortest_lived[['PRESIDENT', 'YEAR_OF_BIRTH', 'LIVED_YEARS', 'LIVED_MONTHS', 'LIVED_DAYS']])

def my_mode(arr):
    counts = {}
    for i in arr:
        if i in counts:
            counts[i] += 1
        else:
            counts[i] = 1
    max_count = max(counts.values())
    if max_count == 1:
        return np.nan
    else:
        return [k for k, v in counts.items() if v == max_count]

class Plotter:
    def __init__(self, df):
        self.df = df
    
    def plot_distribution(self):
        plt.hist(self.df['LIVED_DAYS'], bins=10)
        plt.xlabel('Lived Days')
        plt.ylabel('Frequency')
        plt.show()

def main(filename):
    try:
        # Create an instance of the Reader class
        reader = Reader(filename)

        # Read the CSV file
        df = reader.read_csv()
        df = reader.add_variables(df)

        # Pass the data from the CSV file into the writer and the plotter
        writer = Writer(df)
        writer.add_variables()
        writer.write_output()
        writer.write_statistics()

        plotter = Plotter(df)
        plotter.plot_distribution()

    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        main(filename)
    else:
        print("Usage: python Presidents.py <filename>")