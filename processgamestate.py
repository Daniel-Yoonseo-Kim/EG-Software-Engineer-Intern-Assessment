import pandas as pd
import json

class ProcessGameState:
    def __init__(self, file_path):
        self.data = self.load_data(file_path)

    @staticmethod
    def load_data(file_path):
        return pd.read_parquet(file_path)

    def extract_weapon_classes(self):
        # Extract weapon classes from the inventory json column
        weapon_classes = []
        i = 0
        for _, row in self.data.iterrows():
            if row['inventory'] is not None:
                inventory_dump = json.dumps(row['inventory'].tolist())
                inventory = json.loads(inventory_dump)
                for item in inventory:
                    weapon_classes.append(item['weapon_class'])
        return weapon_classes
