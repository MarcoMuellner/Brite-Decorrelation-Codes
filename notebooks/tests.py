import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from common import *
import warnings

from notebooks.common.statistics import AnalyzeStar

analysis = AnalyzeStar(1)
analysis.load_data()
result = analysis.process_stars()
print(result)
