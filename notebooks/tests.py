from common import *
import warnings

"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stars = load(9)
    for star in stars:
        combine_data(star.get_all_data_sets(star.results[0]))

"""
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stars = load(9)
    data = stars[0].get_data(stars[0].results[0])
    data.to_periodogram().plot()

