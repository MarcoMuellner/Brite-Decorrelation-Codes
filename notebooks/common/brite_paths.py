from abc import abstractproperty
from typing import IO, Union
import matplotlib.pyplot as plt
from astropy.stats import LombScargle
from astropy.units import cds

from .setup import *
from typing import Dict, List
import lightkurve as lk
from lightkurve.lightcurve import LightCurve
from lightkurve.periodogram import Periodogram
import numpy as np
from astropy.time import Time
from astropy import units as u
from astroquery.simbad import Simbad
import re

Simbad.add_votable_fields('otype', 'sp', 'flux(V)')

default_result_entry = 'all'

def binning(time, mag, period, num):
    time = (time%period)/period# (1/0.5988495842998753)*0.5988495842998753
    bins = []
    means = []
    sds = []
    bins.append(0)
    ind = np.where(np.logical_and(time >= 0, time <= 0.5 / num))
    means.append(np.mean(mag[ind]))
    sds.append(np.std(mag[ind]) / np.sqrt(len(mag[ind])))
    for i in range(num - 1):
        ind = np.where(np.logical_and(time >= (i + 0.5) / num, time <= (i + 1.5) / num))
        if ind[0].size > 0:
            bins.append((i + 1) / num)
            means.append(np.mean(mag[ind]))
            sds.append(np.std(mag[ind]))
    bins.append(1)
    ind = np.where(np.logical_and(time >= (num - 0.5) / num, time <= 1))
    means.append(np.mean(mag[ind]))
    sds.append(np.std(mag[ind]))
    return np.array(bins), np.array(means), np.array(sds)


def combine_data(data_list: List['Data']):
    if len(data_list) == 0:
        print("No data provided!")
        return

    target_path = data_list[0].folderpath

    satellites = list(set([i.satellite for i in data_list if not i.combined]))
    for satellite in satellites:
        files = []
        sat_data = []
        for i in data_list:
            if not (i.satellite == satellite and not i.combined) or i.filename in files:
                continue

            files.append(i.filename)
            sat_data.append(i)

        if len(sat_data) == 1:
            continue

        filename = f"{sat_data[0].starname}_{sat_data[0].field}_{satellite}_{'_'.join([str(i.setup) for i in reversed(sat_data)])}_{sat_data[0].dr}"

        raw_data = np.hstack([i.raw_data for i in sat_data])
        try:
            ave_data = np.hstack([i._ave_raw_data for i in sat_data if i._ave_raw_data is not None])
        except ValueError:
            print("No valid ave data!")
            ave_data = None

        np.savetxt(os.path.join(target_path, filename + "_merged_.ndat"), raw_data.T)
        if ave_data is not None:
            np.savetxt(os.path.join(target_path, filename + "_merged_.ave"), ave_data.T)
        print(f"Saving {filename} in {target_path}")


class Data:
    def __init__(self, path: str, star_obj: 'Star') -> None:
        self._path = path
        self._filename = path.split("/")[-1]
        self._ave_path = os.path.join(os.path.dirname(path), self._filename.replace("ndat", 'ave'))

        parser = re.findall(r'(HD\d+)_(\d+-\w+-\w+-\d+)_([a-zA-Z]*)_([\d_-]+)_*([A-Za-z]*)', self._filename)
        self._starname = parser[0][0]
        self._field = parser[0][1]
        self._satellite = parser[0][2]

        if "-" in parser[0][3]:
            nums = parser[0][3].split("-")
            nums = nums[:-1] + nums[-1][:-1].split("_")
        else:
            nums = parser[0][3].split("_")

        if len(nums[-1]) == 0:
            nums = nums[:-1]

        self._setup = nums[:-1]
        self._dr = nums[-1]

        if "merged_" in self._path or len(self._setup) != 1:
            self._setup = [int(i) for i in self._setup]
            self._combined = True
        else:
            self._setup = int(self._setup[0])
            self._combined = False

        """
        if len(self._setup) == 1:
            self._setup = int(self._setup[0])
            self._combined = False
        else:
            self._setup = [int(i) for i in self._setup]
            self._combined = True
        """

        self._star = star_obj

        try:
            self._raw_data = np.loadtxt(path).T
            self._raw_data[1] = self._raw_data[1] - np.mean(self._raw_data[1])
            self._lk_obj = lk.LightCurve(time=Time(self._raw_data[0], format='jd'), flux=self._raw_data[1] * u.mag,
                                         flux_err=self._raw_data[2] * u.mag)
        except IndexError:
            raise ValueError()

        try:
            self._ave_raw_data = np.loadtxt(re.sub(r'_part\d+', '', self._ave_path)).T
        except:
            print(f"No ave file found for {self._filename}")
            self._ave_raw_data = None

        if self._ave_raw_data is not None:
            try:
                self._ave_lk_obj = lk.LightCurve(time=Time(self._ave_raw_data[0], format='jd'),
                                                 flux=self._ave_raw_data[1] / 1000 * u.mag,
                                                 flux_err=self._ave_raw_data[2] / 1000 * u.mag)
            except TypeError:
                new_data = []
                for i in self._ave_raw_data:
                    new_data.append([i])
                self._ave_raw_data = np.array(new_data)
                self._ave_lk_obj = lk.LightCurve(time=Time(self._ave_raw_data[0], format='jd'),
                                                 flux=self._ave_raw_data[1] / 1000 * u.mag,
                                                 flux_err=self._ave_raw_data[2] / 1000 * u.mag)
        else:
            self._ave_lk_obj = None

    def __cmp__(self, other: 'Data'):
        return self.setup >= other.setup

    def __lt__(self, other: 'Data'):
        return self.setup < other.setup

    def __le__(self, other: 'Data'):
        return self.setup <= other.setup

    @property
    def filename(self):
        return self._filename

    @property
    def combined(self):
        return self._combined

    @property
    def star(self):
        return self._star

    @property
    def dr(self):
        return self._dr

    @property
    def folderpath(self):
        return os.path.dirname(self._path)

    @property
    def starname(self):
        return self._starname

    @property
    def field(self):
        return self._field

    @property
    def satellite(self):
        return self._satellite

    @property
    def setup(self):
        return self._setup

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
        return np.sqrt(np.sum(np.power(self._raw_data[1] - np.median(self._raw_data[1]), 2)) / len(self._raw_data[1]))

    @property
    def ptp_scatter(self):
        return np.sqrt(
            np.sum(np.power(self._raw_data[1][:-1] - self._raw_data[1][1:], 2)) / len(self._raw_data[1][:-1]))

    def noise(self, num_datapoints=500):
        return np.mean(self.to_periodogram().power[-num_datapoints:])

    def __str__(self) -> str:
        return self._starname + " -> " + self._path.split("/")[-1]

    def __repr__(self) -> str:
        return self.__str__()

    def plot(self, **kwargs):
        ax = self._lk_obj.plot(**kwargs)
        ax.set_ylabel("Amplitude [mag]")
        ax.set_ylim(ax.get_ylim()[::-1])

    def scatter(self, **kwargs):
        ax = self._lk_obj.scatter(**kwargs, alpha=0.6)
        ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_ylabel("Amplitude [mag]")
        if self._ave_raw_data is not None:
            self._ave_lk_obj.scatter(**kwargs, c='r', ax=ax, s=10)

    def phasephold(self, period = 1, num_bins = 0, plot_ave = True, show_errors = False, bin_color = 'y'):
        fig, ax = plt.subplots()
        ax.plot((self._lk_obj.time.value%period)/period, self._lk_obj.flux.value, 'ko', ms = 0.5, alpha = 0.5, zorder = 1)
        ax.plot((self._lk_obj.time.value%period)/period + 1, self._lk_obj.flux.value, 'ko', ms = 0.5, alpha = 0.5, zorder = 1)
        if plot_ave:
            try:
                ax.plot((self._ave_lk_obj.time.value % period) / period, self._ave_lk_obj.flux.value, color='r', ls='', marker='o', ms=1.5,
                               alpha=0.75, zorder = 1)
                ax.plot((self._ave_lk_obj.time.value % period) / period + 1, self._ave_lk_obj.flux.value, color='r', ls='', marker='o',
                               ms=1.5, alpha=0.75, zorder = 1)
            except:
                pass
        if num_bins != 0:

            if plot_ave:
                try:
                    bins, means, sds = binning(self._ave_lk_obj.time.value, self._ave_lk_obj.flux.value, period, num_bins)
                    if show_errors:
                        ax.errorbar(bins, means, yerr = sds, color =  bin_color,ls = '', capsize = 5, capthick = 2, zorder = 5)
                        ax.errorbar(bins + 1, means, yerr = sds, color =  bin_color,ls = '', capsize = 5, capthick = 2, zorder = 5)
                    ax.plot(bins, means, bin_color + 'o--', ms=5, zorder = 5)
                    ax.plot(bins + 1, means, bin_color + 'o--', ms=5, zorder = 5)
                except:
                    bins, means, sds = binning(self._lk_obj.time.value, self._lk_obj.flux.value, period, num_bins)
                    if show_errors:
                        ax.errorbar(bins, means, yerr=sds, color= bin_color, ls = '', capsize = 5, capthick = 2, zorder = 5)
                        ax.errorbar(bins + 1, means, yerr=sds, color= bin_color,ls = '', capsize = 5, capthick = 2, zorder = 5)
                    ax.plot(bins, means, bin_color + 'o--', ms=5, zorder = 5)
                    ax.plot(bins + 1, means, bin_color + 'o--', ms=5, zorder = 5)

        ax.invert_yaxis()

        ax.set_xlabel("phase P={:3f} d".format(period))
        ax.set_ylabel("Magnitude")





    def to_periodogram(self, method='lombscargle', minimum_frequency=0, maximum_frequency=10, **kwargs) -> Periodogram:
        nyquist = 1/(2*np.median(np.diff(self._raw_data[0])))
        ls = LombScargle(self._raw_data[0],self._raw_data[1],normalization='psd')

        f, p = ls.autopower(minimum_frequency=minimum_frequency, maximum_frequency=maximum_frequency,
                            samples_per_peak=10, nyquist_factor=1)

        # normalization of psd in order to get good amplitudes
        p = np.sqrt(4 / len(self._raw_data[0])) * np.sqrt(p)

        # removing first item
        p = p[1:]
        f = f[1:]

        return Periodogram(f*(1/cds.d),p*u.mag,nyquist=nyquist)

    def fold(self, period=None, epoch_time=None, epoch_phase=0, wrap_phase=None, normalize_phase=False):
        return self._lk_obj.fold(period, epoch_time, epoch_phase, wrap_phase, normalize_phase)

    @property
    def lk(self):
        return self._lk_obj

    @property
    def lk_ave(self):
        return self._ave_lk_obj


class Star:
    def __init__(self, config_dict: Dict[str, str], path: str, field: int) -> None:
        self._config_dict = config_dict
        self._path = path
        self._results = [i for i in os.listdir(path) if os.path.isdir(i) and not i.startswith(".")]
        if len(self._results) == 0:
            self._results = [default_result_entry]
        self._field = field
        self._name = self._path.split("/")[-1].replace("_", " ")
        self._number = int(re.findall(r'\d+', self._name)[0])

        objects = self._get_objects(self.results[0])

        try:
            if objects is not None:
                object_used = objects[list(objects.keys())[0]][0]
                parser = re.findall(r'(HD\d+)_(\d+-\w+-\w+-\d+)_([a-zA-Z]*)_([\d_]+)_*([A-Za-z]*)', object_used)
                self._field_name = parser[0][1]
            else:
                self._field_name = None
        except IndexError:
            self._field_name = None

    def __lt__(self, other: 'Star'):
        return self._number < other._number

    def __le__(self, other: 'Star'):
        return self._number <= other._number

    @property
    def field_name(self):
        return self._field_name

    @property
    def name(self):
        return self._name

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

    def _get_objects(self, result_path) -> Union[None, Dict[int, str]]:
        if result_path not in self._results:
            raise AttributeError(f"Please use one of the following result datasets:\n {self._results}")

        if result_path == default_result_entry:
            used_path = self._path
        else:
            used_path = os.path.join(self._path, result_path)
        objects = {}

        counter = 1

        for root, dir, files in os.walk(used_path):
            files = [i for i in files if i.endswith('ndat')]
            for file in files:
                objects[counter] = (file, os.path.join(root, file))
                counter += 1

        if len(objects.keys()) == 0:
            print("No available data!")
            return None

        return objects

    def get_all_data_sets(self, result_path: str):
        objects = self._get_objects(result_path)
        if objects is None:
            return []

        data_list = []

        for i in objects.values():
            try:
                data_list.append(Data(i[1], self))
            except ValueError:
                print(f"No valid data for {i[1]}")

        return data_list

    def get_data(self, result_path: str):
        objects = self._get_objects(result_path)

        if objects is None:
            return None

        if len(objects.keys()) == 1:
            object_used = objects[list(objects.keys())[0]]
        else:
            while (True):
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

                object_used = objects[object_nr]
                break

        return Data(object_used[1], self)

    def __str__(self) -> str:
        return self._path.split("/")[-1].replace("_", " ")

    def __repr__(self) -> str:
        return self.__str__()


def load(field: int = None) -> List[Star]:
    if (field is None):
        field = input("Please enter a field: ")
        try:
            field = int(field)
        except Exception as e:
            print("Please enter a valid number")
            raise AttributeError("Please enter a valid number for a field!")

    config_dict = get_config()

    field_path = os.path.join(config_dict[ValueDefined.decorrelation_path.value], "Decorrelations", f"Field {field}")

    if not os.path.exists(field_path):
        raise IOError(f"Path {field_path} doesn't exist!")

    star_list = []

    if len([i for i in os.listdir(field_path) if i.startswith("HD")]) == 0:
        field_path = os.path.join(field_path, 'RESULTS')

    for i in os.listdir(field_path):
        if not i.startswith("HD"):
            continue
        star_list.append(Star(config_dict, os.path.join(field_path, i), field))
    star_list = sorted(star_list)
    return star_list
