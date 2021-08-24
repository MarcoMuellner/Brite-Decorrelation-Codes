from common import *
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    stars = load(14)
    for star in stars:
        combine_data(star.get_all_data_sets(star.results[0]))

