"""
    Automatic tests for the smhi_lib
"""
# pylint: disable=C0302,W0621,R0903, W0212

from datetime import datetime
from typing import List

import aiohttp
import pytest
from smhi.smhi_lib import (Smhi, SmhiForecast, SmhiAPIBase, SmhiAPI, SmhiForecastException)
from smhi import smhi_lib

import logging

@pytest.fixture
def smhi() -> Smhi:
    """Returns the smhi object."""
    return Smhi('17.041', '62.34198', api=FakeSmhiApi())

@pytest.fixture
def smhi_real() -> Smhi:
    """Returns the smhi object."""
    #return Smhi('17.661578', '59.514065')
    return Smhi('17.03078', '62.3398599') #Bällsta
    
@pytest.fixture
def smhi_forecasts(smhi) -> List[SmhiForecast]:
    """Returns the smhi object."""
    return smhi.get_forecast()

@pytest.fixture
def first_smhi_forecast(smhi) -> SmhiForecast:
    """Returns the smhi object."""
    return smhi.get_forecast()[1]

@pytest.fixture
def first_smhi_forecast2(smhi) -> SmhiForecast:
    """Returns the smhi object."""
    return smhi.get_forecast()[2]


@pytest.mark.asyncio
async def test_provide_session_constructor() -> None:
    """Test the constructor that provides session."""
    session = aiohttp.ClientSession()
    api = Smhi("1.1234567", "1.9876543",
               session=session,
               api=FakeSmhiApi())

    await session.close()
    assert api._api.session

def test_max_six_digits_round() -> None:
    """Test the max six digits allowed."""
    api = Smhi("1.1234567", "1.9876543")
    assert api._latitude == "1.987654"
    assert api._longitude == "1.123457"


def test_nr_of_items(smhi_forecasts) -> None:
    """Tests the number of items returned matches the inputdata."""
    assert len(smhi_forecasts) == 12

def test_temperature(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.temperature == 17

def test_temperature_max(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.temperature_max == 17

def test_temperature_min(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.temperature_min == 7

def test_humidity(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.humidity == 55


def test_pressure(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.pressure == 1024


def test_thunder(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.thunder == 33


def test_cloudiness(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.cloudiness == 50


def test_precipitation(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.precipitation == 1


def test_mean_precipitation(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.mean_precipitation ==  0.08333333333333333


def test_total_precipitation(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.total_precipitation ==  2.0

def test_wind_speed(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.wind_speed == 1.9


def test_wind_direction(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.wind_direction == 134


def test_wind_gust(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.wind_gust == 4.7


def test_horizontal_visibility(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.horizontal_visibility == 50


def test_symbol(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.symbol == 1


def test_valid_time(first_smhi_forecast):
    '''test'''
    assert first_smhi_forecast.valid_time == datetime(2018, 9, 1, 15, 0, 0)


def test_cloudiness_when_inconclusive(first_smhi_forecast2):
    '''test'''
    assert first_smhi_forecast2.cloudiness == 100


def test_use_abstract_base_class():
    '''test the not implemented stuff'''
    with pytest.raises(NotImplementedError):
        test = SmhiAPIBase()
        test.get_forecast_api('17.00', '62.1')


def test_smhi_integration_test():
    '''Only test that uses the actual service. Make sure service is up if fails'''
    api = SmhiAPI()
    forecast = api.get_forecast_api('17.00', '62.1')
    assert forecast is not None


@pytest.mark.asyncio
async def test_smhi_async_integration_test():
    '''Only test that uses the actual service. Make sure service is up if fails'''
    api = SmhiAPI()
    forecast = await api.async_get_forecast_api('17.00', '62.1')
    assert forecast is not None


@pytest.mark.asyncio
async def test_smhi_async_integration_test_use_session():
    '''Only test that uses the actual service. Make sure service is up if fails'''
    api = SmhiAPI()
    api.session = aiohttp.ClientSession()
    forecast = await api.async_get_forecast_api('17.041326', '62.339859')
    assert forecast is not None
    await api.session.close()

@pytest.mark.asyncio
async def test_smhi_async_get_forecast_integration(smhi):
    '''test the async stuff'''
    forecast = await smhi.async_get_forecast()
    assert forecast[0] is not None
    assert forecast is not None

@pytest.mark.asyncio
async def test_smhi_async_get_forecast_integration2(smhi_real):
    '''test the async stuff'''
    forecast = await smhi_real.async_get_forecast()
    assert forecast[0] is not None
    assert forecast is not None
    print(forecast[0].temperature)
    print(forecast[1].temperature)

@pytest.mark.asyncio
async def test_smhi_async_get_forecast_integration_use_session(smhi):
    '''test the async stuff'''
    smhi.session = aiohttp.ClientSession()
    forecast = await smhi.async_get_forecast()

    assert forecast[0] is not None
    assert forecast is not None

    await smhi.session.close()

@pytest.mark.asyncio
async def test_async_use_abstract_base_class():
    '''test the not implemented stuff'''
    with pytest.raises(NotImplementedError):
        test = SmhiAPIBase()
        await test.async_get_forecast_api('17.00', '62.1')


@pytest.mark.asyncio
async def test_async_error_from_api():
    '''test the async stuff'''
    api = SmhiAPI()
    #Faulty template
    smhi_lib.APIURL_TEMPLATE = "https://opendata-download-metfcst.smhi.se/api/category"\
                       "/pmp3g/version/2/geotype/point/lon/{}/lat/{}/dataa.json"

    smhi_error = Smhi('17.00', '62.1', api=api)
    with pytest.raises(SmhiForecastException):
        await smhi_error.async_get_forecast()

    

# Might have to rewrite this test at some point

# def test_precipitation_mean_value(smhi):
#     """Test average precipitation calulation.

#     Average for the forecast is calculated the average
#     for the whole day.
#     """
#     fake_api = FakeSmhiApi()
#     fake_forecast = fake_api.get_forecast_api(' ', ' ')
#     total_mean_precipitation = -1.0
#     for forecast in fake_forecast['timeSeries']:
#         valid_time = datetime.strptime(forecast['validTime'], "%Y-%m-%dT%H:%M:%SZ")
#         if (valid_time.day == 8 and valid_time.hour > 0) or \
#            (valid_time.day == 9 and valid_time.hour == 0):
#             print(valid_time)
#             for param in forecast['parameters']:
#                 if param['name'] == 'pmean':
#                     print(float(param['values'][0]))
#                     if total_mean_precipitation < 0:
#                         total_mean_precipitation = float(param['values'][0])
#                     else:
#                         total_mean_precipitation = (
#                             total_mean_precipitation + float(param['values'][0]))/2.0

#     forecast = smhi.get_forecast()
#     assert forecast[8].mean_precipitation == total_mean_precipitation

#
#  Use this test for future debugs
# 

# @pytest.mark.asyncio
# async def test_real_data(smhi_real):

#     w= open("C:\\temp\\forecast_total.txt","w+")    
#     forecast = await smhi_real.async_get_forecast()
#     for f in forecast:
#         w.write("time: {}".format(f.valid_time)+"\r\n")
#         w.write("temp_max: {}".format(f.temperature_max)+"\r\n")
#         w.write("temp_min: {}".format(f.temperature_min)+"\r\n")
#         w.write("totalPre: {}".format(f.total_precipitation)+"\r\n")
#         w.write("meanPre: {}".format(f.mean_precipitation)+"\r\n")
#         w.write("----")

#     w.close()    
#     assert True == False

class FakeSmhiApi(SmhiAPIBase):
    '''Implements fake class to return API data'''

    async def async_get_forecast_api(self, longitude: str, latitude: str) -> {}:
        """Real data from the version code works from"""
        return self.get_forecast_api(longitude, latitude)

    def get_forecast_api(self, longitude: str, latitude: str) -> {}:
        """Real data from the version code works from"""
        return {
            "approvedTime": "2018-09-01T14:06:18Z",
            "referenceTime": "2018-09-01T14:00:00Z",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    [
                        16.024394,
                        63.341937
                    ]
                ]
            },
            "timeSeries": [
                {
                    "validTime": "2018-09-01T15:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                17
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                134
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.9
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                55
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                33
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.7
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T16:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                9
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                16.1
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                140
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                64
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.8
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T17:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                14.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                134
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                75
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.2
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T18:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                13
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                190
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                82
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T19:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.1
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                11.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                222
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                87
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T20:00:00Z",
                    "parameters": [
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.3
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9.6
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                228
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T21:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                8.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                11.1
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                239
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T22:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                7.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                48.1
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                231
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-01T23:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                6.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                48.1
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                219
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.9
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                12
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                214
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                87
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T01:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                5.6
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                211
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                87
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T02:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.1
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                5.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                212
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                89
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T03:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                4.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                48.3
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                223
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                89
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T04:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                5.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                48.2
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                236
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T05:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                48.2
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                234
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                86
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                8.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                225
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                82
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T07:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1027
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                11.1
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                249
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                73
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T08:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1027
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                13.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                127
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                62
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T09:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                15.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                32.4
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                117
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                53
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T10:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                18.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                147
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                46
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T11:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                19.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                201
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                43
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.2
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20.6
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                203
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                43
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                9
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T13:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                195
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.9
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                43
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.9
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T14:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.3
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                196
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.9
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                43
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T15:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026.1
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                36.2
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                191
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.6
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                48
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T16:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                19.1
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                142
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                55
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T17:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                17.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                141
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                66
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T18:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                15.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                146
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                79
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T19:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                13.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                142
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                85
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.3
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T20:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                12.3
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                127
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                82
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T21:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                115
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                79
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T22:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.1
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                90
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                77
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-02T23:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9.3
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                19.4
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                95
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                75
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                8.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                104
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                73
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T01:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                116
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                74
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T02:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.2
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                7.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                112
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                76
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.9
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T03:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                7.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                109
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                78
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T04:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                105
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                81
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T05:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                80
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.6
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                80
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                124
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                74
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T07:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1023.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                13.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                217
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                66
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                7.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T08:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1023.3
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                15.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                28.5
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                219
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                60
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                7.9
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T09:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1022.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                17.4
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                220
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                52
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T10:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1022.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                19
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                217
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                48
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T11:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1022
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20.3
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                214
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                48
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                9.2
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1021.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                21.3
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                212
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.6
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                49
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                9.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T15:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                20.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                209
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                51
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T18:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                15
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                199
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.6
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                70
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.1
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-03T21:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                11.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                223
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                80
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-04T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.2
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.6
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                263
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                84
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.3
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                1
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-04T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                12.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                310
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                86
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-04T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                19.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                353
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.4
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                60
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-04T18:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1021.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                14.3
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                333
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                81
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-05T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1023
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                11.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                4.9
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                342
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.9
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                95
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-05T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1023.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                12.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                32.8
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                353
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                87
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.3
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-05T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1022.5
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                18
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                67
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                61
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-05T18:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1021.6
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                12.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                131
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                91
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.2
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-06T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1019.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                11.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                7.1
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                344
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                94
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-06T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1017.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                12.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                28.2
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                316
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                91
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                4.5
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-06T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1015.2
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                16
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                19.5
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                187
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                75
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                6
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-06T18:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1013.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                13.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                50
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                144
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                91
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                6
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                3.2
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                -9
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-07T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1017.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.2
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                23.6
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                331
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                92
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                7.2
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.3
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                19
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-07T06:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1018.3
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10.5
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                35.4
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                338
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.8
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                6
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-07T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1018.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                14.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                38
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                356
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                65
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                10.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-08T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1020.9
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                10
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                31.3
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                339
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2.5
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                85
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.6
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1.3
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.2
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                2
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-08T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1022.4
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                14.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                40.6
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                14
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                66
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                8
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                11
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                6
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-09T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1024.3
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9.7
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                28.7
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                356
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.7
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                88
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                7.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1.9
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-09T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                15.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                42.8
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                35
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.1
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                64
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                9.8
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                1.2
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-10T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.7
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                27.3
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                328
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                91
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                5
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                6.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.9
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-10T12:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1025.8
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                16.8
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                44
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                55
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                0.3
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                62
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                7
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                8.4
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.7
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                4
                            ]
                        }
                    ]
                },
                {
                    "validTime": "2018-09-11T00:00:00Z",
                    "parameters": [
                        {
                            "name": "msl",
                            "levelType": "hmsl",
                            "level": 0,
                            "unit": "hPa",
                            "values": [
                                1026
                            ]
                        },
                        {
                            "name": "t",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "Cel",
                            "values": [
                                9.9
                            ]
                        },
                        {
                            "name": "vis",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "km",
                            "values": [
                                27.6
                            ]
                        },
                        {
                            "name": "wd",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "degree",
                            "values": [
                                308
                            ]
                        },
                        {
                            "name": "ws",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                1.2
                            ]
                        },
                        {
                            "name": "r",
                            "levelType": "hl",
                            "level": 2,
                            "unit": "percent",
                            "values": [
                                92
                            ]
                        },
                        {
                            "name": "tstm",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "tcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                4
                            ]
                        },
                        {
                            "name": "lcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "mcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "hcc_mean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "octas",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "gust",
                            "levelType": "hl",
                            "level": 10,
                            "unit": "m/s",
                            "values": [
                                5.7
                            ]
                        },
                        {
                            "name": "pmin",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pmax",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.8
                            ]
                        },
                        {
                            "name": "spp",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "percent",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "pcat",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        },
                        {
                            "name": "pmean",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0.1
                            ]
                        },
                        {
                            "name": "pmedian",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "kg/m2/h",
                            "values": [
                                0
                            ]
                        },
                        {
                            "name": "Wsymb2",
                            "levelType": "hl",
                            "level": 0,
                            "unit": "category",
                            "values": [
                                3
                            ]
                        }
                    ]
                }
            ]
        }