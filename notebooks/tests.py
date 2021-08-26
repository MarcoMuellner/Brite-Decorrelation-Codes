from matplotlib import pyplot as plt

from common import *
import warnings


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fields = [9,10,11,12,14]
    for field in fields:
        stars = load(field)
        for star in stars:
            combine_data(star.get_all_data_sets(star.results[0]))

"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fields = [9,10,11,12,14]
    for field in fields:
        print(field)
        stars = load(fields[1])
        result_data = []
        lines = ""
        for star in stars:
            data = star.get_all_data_sets(star.results[0])
            merged_data = [i for i in data if i.combined and "merged" in i.filename]
            print([i.noise() for i in merged_data])
#    data = stars[0].get_data(stars[0].results[0])
#    data.to_periodogram().plot()
"""

