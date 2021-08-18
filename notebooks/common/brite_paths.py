from abc import abstractproperty
from typing import IO
from .setup import *
from typing import Dict,List
import lightkurve as lk
from lightkurve.lightcurve import LightCurve
from lightkurve.periodogram import Periodogram
import numpy as np
from astropy.time import Time
from astropy import units as u
from astroquery.simbad import Simbad


class Data:
    def __init__(self,path : str, star_obj : 'Star') -> None:
        self._path = path
        self._star = star_obj

        self._raw_data = np.loadtxt(path).T
        self._lk_obj = lk.LightCurve(time=Time(self._raw_data[0],format='jd'),flux=self._raw_data[1]*u.mag,flux_err=self._raw_data[2]*u.mag)

    @property
    def star(self):
        return self._star
    
    @property
    def path(self):
        return self._path
    
    @property
    def time(self):
        return self._raw_data[0]

    @property
    def flux(self):
        return self._raw_data[1]

    @property
    def flux_err(self):
        return self._raw_data[2]

    @property
    def raw_data(self):
        return self._raw_data

    def __str__(self) -> str:
        return self._star.__str__() + " -> " + self._path.split("/")[-1]

    def __repr__(self) -> str:
        return self.__str__()

    def plot(self,**kwargs):
        self._lk_obj.plot(**kwargs)

    def scatter(self,**kwargs):
        self._lk_obj.scatter(**kwargs)

    def to_periodogram(self,method='lombscargle',**kwargs) -> Periodogram:
        return self._lk_obj.to_periodogram(method,**kwargs)

class Star:
    def __init__(self,config_dict : Dict[str,str],path : str,field : int) -> None:
        self._config_dict = config_dict
        self._path = path
        self._results = os.listdir(path)
        self._field = field
    
    @property
    def config_dict(self):
        return self._config_dict

    @property
    def path(self):
        return self._path

    @property
    def results(self) -> List[str]:
        return self._results

    @property
    def simbad(self):
        return Simbad.query_object(self.__str__())
    
    def get_data(self,result_path : str):
        if result_path not in self._results:
            raise AttributeError(f"Please use one of the following result datasets: {self._results}")
        
        used_path = os.path.join(self._path,result_path)
        objects = {}

        counter = 1

        for root,dir,files in os.walk(used_path):
            files = [i for i in files if i.endswith('ndat')]
            for file in files:
                objects[counter] = (file,os.path.join(root,file))
                counter +=1
        
        if len(objects.keys()) == 0:
            print("No available data!")
            return None

        if len(objects.keys()) == 1:
            object_used = objects[list(objects.keys())[0]]
        else:
            while(True):
                str_objects = "\n".join([f'{i}): {objects[i][0]}' for i in objects.keys()])

                object_nr = input(f"Please choose a dataset by entering a number: {str_objects}")
                try:
                    object_nr = int(object_nr)
                except:
                    print("Please enter a number!")
                    continue
                    
                if object_nr not in objects.keys():
                    print("Please enter a valid number from the list")
                    continue

                object_used= objects[object_nr]
                break

        return Data(object_used[1],self)


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

    field_path = os.path.join(config_dict[ValueDefined.decorrelation_path.value],"Decorrelations",f"Field {field}")

    if not os.path.exists(field_path):
        raise IOError(f"Path {field_path} doesn't exist!")
    
    star_list = []
    for i in os.listdir(field_path):
        if not i.startswith("HD"):
            continue
        star_list.append(Star(config_dict,os.path.join(field_path,i),field))
    
    return star_list


          



