from abc import abstractproperty
from typing import IO
from setup import *
from typing import Dict,List
import lightkurve as lk
import numpy as np
from astropy.time import Time

class Data:
    def __init__(self,path : str, star_obj : 'Star') -> None:
        self._path = path
        self._star = star_obj

        self._raw_data = np.loadtxt(path).T
        self._lk_obj = lk.LightCurve(Time(self._raw_data[0],format='jd'))

    @property
    def star(self):
        return self._star
    
    @property
    def path(self):
        return self._path

    def __str__(self) -> str:
        return self._star.__str__() + " -> " + self._path.split("/")[-1]

    def __repr__(self) -> str:
        return self.__str__()

class Star:
    def __init__(self,config_dict : Dict[str,str],path : str) -> None:
        self._config_dict = config_dict
        self._path = path
        self._results = os.listdir(path)
    
    @property
    def config_dict(self):
        return self._config_dict

    @property
    def path(self):
        return self._path

    @property
    def results(self) -> List[str]:
        return self._results
    
    def get_data(self,result_path : str):
        if result_path not in self._results:
            raise AttributeError(f"Please use one of the following result datasets: {self._results}")
        
        used_path = os.path.join(self._path,result_path)
        objects = {}
        for i,j in enumerate(os.listdir(used_path)):
            if not j.endswith('ndat'):
                continue

            objects[i] = j
        
        if len(objects.keys()) == 0:
            print("No available data!")
            return None

        if len(objects.keys) == 1:
            object_used = objects[objects.keys[0]]
        else:
            while(True):
                objects = "\n".join([f'{i}): {objects[i]}' for i in objects.keys()])

                object_nr = input(f"Please choose a dataset by entering a number: {objects}")
                try:
                    object_nr = int(object_nr)
                except:
                    print("Please enter a number!")
                    continue
                    
                if object_nr not in objects.keys():
                    print("Please enter a valid number from the list")
                    continue

                object_used= objects[object_nr]
        
        full_path = os.path.join(used_path,object_used,self)


    def __str__(self) -> str:
        return self._path.split("/")[-1].replace("_"," ")
    
    def __repr__(self) -> str:
        return self.__str__()

def load(field : int = None) -> List[Star]:
    if(field is None):
        field = input("Please enter a field: ")
        try:
            field = int(field)
        except Exception as e:
            print("Please enter a valid number")
            raise AttributeError("Please enter a valid number for a field!")

    config_dict = get_config()

    field_path = os.path.join(config_dict[ValueDefined.decorrelation_path.value],f"Field {field}")

    if not os.path.exists(field_path):
        raise IOError(f"Path {field_path} doesn't exist!")
    
    star_list = []
    for i in os.listdir(field_path):
        if not i.startswith("HD"):
            continue
        star_list.append(Star(config_dict,i))
    
    return star_list

          



