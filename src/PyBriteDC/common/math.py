from typing import Callable

import numpy as np
from astropy.stats import LombScargle
from astropy import units as u
from lightkurve.periodogram import Periodogram # type: ignore
from astropy.units import cds


def lightcurve_check(func: Callable) -> Callable: # type: ignore
    def wrapper(*args, **kwargs): # type: ignore
        # Check the dimensions of the lightcurve
        if args[0].ndim != 2:
            raise ValueError("The lightcurve must be a 2D array")

        # Check the number of columns in the lightcurve
        if args[0].shape[1] != 2:
            raise ValueError("The lightcurve must have 2 columns")

        return func(*args, **kwargs)

    return wrapper


@lightcurve_check
def periodogram(lightcurve: np.ndarray, minimum_frequency: int = 0, maximum_frequency: int = 10, # type: ignore
                **kwargs) -> Periodogram:
    """
    Calculates the periodogram of a given lightcurve with proper normalization. The periodogram is calculated using the
    Lomb-Scargle algorithm.
    :param lightcurve: The lightcurve to calculate the periodogram for. Dimensions: (n,2)
    :param minimum_frequency: Minimum frequency to calculate the periodogram for.
    :param maximum_frequency: Maximum frequency to calculate the periodogram for.
    :param kwargs: Additional arguments to pass to the lightkurve periodogram function.
    :return: The periodogram of the lightcurve.
    """
    nyquist = 1 / (2 * np.median(np.diff(lightcurve[:, 0])))
    ls = LombScargle(lightcurve[:, 0], lightcurve[:, 1], normalization='psd')

    f, p = ls.autopower(minimum_frequency=minimum_frequency, maximum_frequency=maximum_frequency, nyquist_factor=1,
                        samples_per_peak=10, **kwargs)

    p = np.sqrt(4 / len(lightcurve[:, 0])) * np.sqrt(p)

    # removing first item
    p = p[1:]
    f = f[1:]

    return Periodogram(f * (1 / cds.d), p * u.mag, nyquist=nyquist)


@lightcurve_check
def calculate_rms(lightcurve: np.ndarray) -> float: # type: ignore
    """
    Calculates the RMS of a given lightcurve. The RMS is calculated by taking the square root of the sum of the squared
    values of the lightcurve divided by the number of data points in the lightcurve.
    :param lightcurve: The lightcurve to calculate the RMS of. Dimensions: (n, 2)
    :return: The RMS of the lightcurve.
    """
    mmag_flag = np.median(lightcurve[:, 1] - np.amin(lightcurve[:, 1])) > 100
    flux = lightcurve[:, 1] - np.median(lightcurve[:, 1])
    flux = flux / 1000 if mmag_flag else flux
    return np.sqrt(np.sum(flux ** 2) / len(lightcurve[:, 1]))


@lightcurve_check
def calculate_ptp_scatter(lightcurve: np.ndarray) -> float: # type: ignore
    """
    Calculates the ptp scatter of a given lightcurve. The ptp scatter is calculated by taking the square root of the
    sum of the difference between the n and n+1th point to the power of 2, divided by the number of data points
    in the lightcurve minus 1
    :param lightcurve: The lightcurve to calculate the ptp scatter of. Dimensions: (n, 2)
    :return: The ptp scatter of the lightcurve
    """
    return np.sqrt(np.sum((lightcurve[1:, 1] - lightcurve[:-1, 1]) ** 2) / (len(lightcurve[:, 1]) - 1))


@lightcurve_check
def calculate_noise(lightcurve: np.ndarray, num_datapoints: int = 500) -> float:
    """
    Calculates the noise of a given lightcurve. The noise is calculated by converting the lightcurve into a
    periodogram, and then taking the median of the last num_datapoints point in the power spectrum.
    :param lightcurve: The lightcurve to calculate the noise of. Dimensions: (n, 2)
    :param num_datapoints: The number of points to take the median of. Default: 500
    :return: The noise of the lightcurve
    """
    return np.mean(periodogram(lightcurve).power[-num_datapoints:]).value
