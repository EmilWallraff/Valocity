

class BiKeyDict:
    def __init__(self):
        self.key1_to_value = {}
        self.key2_to_key1 = {}

    def add(self, key1, key2, value):
        if key1 in self.key1_to_value or key2 in self.key2_to_key1:
            raise KeyError("Either key already exists.")
        self.key1_to_value[key1] = value
        self.key2_to_key1[key2] = key1

    def get(self, key):
        if key in self.key1_to_value:
            return self.key1_to_value[key]
        elif key in self.key2_to_key1:
            key1 = self.key2_to_key1[key]
            return self.key1_to_value[key1]
        else:
            raise KeyError("Key not found")

    def remove(self, key):
        if key in self.key1_to_value:
            value = self.key1_to_value.pop(key)
            key2 = next(k2 for k2, k1 in self.key2_to_key1.items() if k1 == key)
            self.key2_to_key1.pop(key2)
        elif key in self.key2_to_key1:
            key1 = self.key2_to_key1.pop(key)
            self.key1_to_value.pop(key1)
        else:
            raise KeyError("Key not found")
