from matplotlib import pyplot as plt

from common import *
import warnings

"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stars = load(10)
    for star in stars:
        combine_data(star.get_all_data_sets(star.results[0]))

"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stars = load(9)
    for star in stars:
        data = star.get_all_data_sets(star.results[0])[0]
        data.to_periodogram()
        print('%.4f'%(data.noise().value*1000) + f" -> {star.name}")
#    data = stars[0].get_data(stars[0].results[0])
#    data.to_periodogram().plot()


