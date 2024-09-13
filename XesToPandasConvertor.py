import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py

class XesToPandasConverter:
    def __init__(self, file_path, chunk_size=1000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.log = pm4py.read_xes(file_path)

    def convert_to_dataframe(self):
        df_list = []
        for i in range(0, len(self.log), self.chunk_size):
            chunk = self.log[i:i + self.chunk_size]
            df_chunk = pm4py.convert_to_dataframe(chunk)
            df_list.append(df_chunk)
        df = pd.concat(df_list, ignore_index=True)
        return df

    def convert_to_html(self):
        df = self.convert_to_dataframe()
        return df.to_html(classes='dataframe table table-striped table-bordered', index=False)
