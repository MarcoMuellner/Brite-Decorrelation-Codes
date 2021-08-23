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

default_result_entry = 'all'

class Data:
    def __init__(self,path : str, star_obj : 'Star') -> None:
        self._path = path
        self._ave_path = os.path.join(os.path.dirname(path),path.split("/")[-1].replace("ndat",'ave'))
        self._star = star_obj

        self._raw_data = np.loadtxt(path).T
        self._ave_raw_data = np.loadtxt(self._ave_path).T
        self._lk_obj = lk.LightCurve(time=Time(self._raw_data[0],format='jd'),flux=(self._raw_data[1] - np.mean(self._raw_data[1]))*u.mag,flux_err=self._raw_data[2]*u.mag)
        self._ave_lk_obj = lk.LightCurve(time=Time(self._ave_raw_data[0],format='jd'),flux=self._ave_raw_data[1]/1000*u.mag,flux_err=self._ave_raw_data[2]/1000*u.mag)

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

    @property
    def datapoints(self):
        return len(self._raw_data[0])

    @property
    def rms(self):
        return np.sqrt(np.sum(np.power(self._raw_data[1]-np.median(self._raw_data[1]),2))/len(self._raw_data[1]))

    @property
    def ptp_scatter(self):
        return np.sqrt(np.sum(np.power(self._raw_data[1][:-1] - self._raw_data[1][1:],2))/len(self._raw_data[1][:-1]))

    def noise(self,num_datapoints = 500):
        return np.mean(self.to_periodogram().power[-num_datapoints:])

    def __str__(self) -> str:
        return self._star.__str__() + " -> " + self._path.split("/")[-1]

    def __repr__(self) -> str:
        return self.__str__()

    def plot(self,**kwargs):
        self._lk_obj.plot(**kwargs)

    def scatter(self,**kwargs):
        ax = self._lk_obj.scatter(**kwargs,alpha=0.6)
        self._ave_lk_obj.scatter(**kwargs,c='r',ax=ax,s=10)

    def to_periodogram(self,method='lombscargle',**kwargs) -> Periodogram:
        return self._lk_obj.to_periodogram(method,**kwargs)

    def fold(self,period=None,epoch_time=None,epoch_phase=0,wrap_phase=None,normalize_phase=False):
        return self._lk_obj.fold(period,epoch_time,epoch_phase,wrap_phase,normalize_phase)

    @property
    def lk(self):
        return self._lk_obj

    @property
    def lk_ave(self):
        return self._ave_lk_obj

class Star:
    def __init__(self,config_dict : Dict[str,str],path : str,field : int) -> None:
        self._config_dict = config_dict
        self._path = path
        self._results = [i for i in os.listdir(path) if os.path.isdir(i) and not i.startswith(".")]
        if len(self._results) == 0:
            self._results = [default_result_entry]
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
            raise AttributeError(f"Please use one of the following result datasets:\n {self._results}")

        if result_path == default_result_entry:
            used_path = self._path
        else:
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

                object_nr = input(f"Please choose a dataset by entering a number:\n {str_objects}")
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

    if len([i for i in os.listdir(field_path) if i.startswith("HD")]) == 0:
        field_path = os.path.join(field_path,'RESULTS')

    for i in os.listdir(field_path):
        if not i.startswith("HD"):
            continue
        star_list.append(Star(config_dict,os.path.join(field_path,i),field))
    
    return star_list
          



