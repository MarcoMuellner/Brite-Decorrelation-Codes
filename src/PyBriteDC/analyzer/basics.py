import os

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad

from PyBriteDC.common import math as mc
from PyBriteDC.models import file as mf
from PyBriteDC.models import observation as mo
from PyBriteDC.prep import combiner as cb
from PyBriteDC.prep import filesystem as fs


customSimbad = Simbad()
customSimbad.add_votable_fields("otype", "sp", "flux(V)", "flux(B)", "ids", "parallax")
extinction_file_path = os.path.join(
    os.path.dirname(__file__), "..", "res", "extinction.txt"
)
extinction_data = np.loadtxt(extinction_file_path, skiprows=16)


def load_field(
    path: str, target_path: str, override_model: bool = False
) -> mo.MergedField:
    """
    Parses a given file path to search for reduced Brite Observations. Then combines each star and satellite
    into a single merged dataset, which is stored in a folder at the same level as path (with a _MERGED postfix).
    The directory structure for the merged data is the same as the original data. It then will continue to
    find the attached metadata for any given star and satellite.

    The method will also look if the _MERGED path already exists, and if a model_data.json file exists. This
    model.json data is instead loaded, if it exists.
    :param override_model: If true, the model_data.json file will be ignored and the data will be reloaded.
    :param path: The path to parse.
    :return:
    """

    if not os.path.exists(target_path):
        os.mkdir(target_path)

    field_stars = fs.find_stars(path)

    field_path = os.path.join(target_path, "Field_" + str(field_stars.field_number))

    if not os.path.exists(field_path):
        os.mkdir(field_path)

    star_objects = []

    for star in field_stars.stars:
        target_star_path = os.path.join(field_path, f"HD_{star.hd_number}")
        if not os.path.exists(target_star_path):
            os.mkdir(target_star_path)

        observations = cb.combine_observations(star)
        simbad_data = customSimbad.query_object(f"HD {star.hd_number}").to_pandas()
        coord = SkyCoord(
            ra=simbad_data["RA"][0],
            dec=simbad_data["DEC"][0],
            unit=(u.hourangle, u.deg),
            frame="icrs",
        )
        width = u.Quantity(0.01, u.deg)
        height = u.Quantity(0.01, u.deg)
        gaia_data = Gaia.query_object_async(
            coordinate=coord, width=width, height=height
        )

        parallax = (
            gaia_data["parallax"].data[0]
            if len(gaia_data["parallax"]) > 0
            else float(simbad_data["PLX_VALUE"][0])
        )
        distance = 1000 / parallax

        closest_index = np.argmin(np.abs(extinction_data[:, 0] - coord.ra.degree))
        extinction = extinction_data[:, 9][closest_index]

        observation_objects = []

        for observation in observations:

            target_observation_path = os.path.join(
                target_star_path,
                f"HD{star.hd_number}_field_{field_stars.field_number}_{observation.satellite.value}_{'-'.join([f'{i}' for i in observation.setup]) if isinstance(observation.setup, list) else observation.setup}",
            )

            for file_name, data in zip(
                [
                    f"{target_observation_path}.orig",
                    f"{target_observation_path}.ndat",
                    f"{target_observation_path}.ave",
                ],
                [observation.orig_data, observation.ndat_data, observation.ave_data],
            ):
                np.savetxt(file_name, data)

            observation_object = mo.MergedSingleObservation(
                ndat_file=f"{target_observation_path}.ndat",
                orig_file=f"{target_observation_path}.orig",
                ave_file=f"{target_observation_path}.ave",
                ndat_datapoints=observation.ndat_data.shape[0],
                orig_datapoints=observation.orig_data.shape[0],
                rms=mc.calculate_rms(observation.ndat_data[:, 0:2]),
                ptp_scatter=mc.calculate_ptp_scatter(observation.ndat_data[:, 0:2]),
                noise=mc.calculate_noise(observation.ndat_data[:, 0:2]),
                rms_per_orbit=mc.calculate_rms(observation.ave_data[:, 0:2]),
                satellite=observation.satellite,
                setup=observation.setup,
            )
            observation_objects.append(observation_object)

        star_object = mo.MergedStar(
            hd_number=star.hd_number,
            path=target_star_path,
            single_observations=observation_objects,
            spectral_type=str(simbad_data["SP_TYPE"][0]),
            b_magnitude=float(simbad_data["FLUX_B"][0]),
            v_magnitude=float(simbad_data["FLUX_V"][0]),
            abs_magnitude=float(simbad_data["FLUX_V"][0])
            - 5 * np.log(distance / 10)
            - extinction,
            parallax=parallax,
            distance=distance,
        )
        star_objects.append(star_object)

    return mo.MergedField(
        path=target_path, stars=star_objects, field_number=field_stars.field_number
    )
