import requests
import json
from datetime import datetime
API_URL = 'https://api.developmentseed.org/satellites/landsat'
def que_land(lat=None, lon=None, start=None, end=None,minc =None, maxc=None, limit = 1000):
    aq_date = 'acquisitionDate:[%s+TO+%s]' % (start, end)
    cloud =  'cloudCoverFull:[%s+TO+%s]' % (minc, maxc)
    add = ('upperLeftCornerLatitude:[%s+TO+1000]+AND+lowerRightCornerLatitude:[-1000+TO+%s]'
           '+AND+lowerLeftCornerLongitude:[-1000+TO+%s]+AND+upperRightCornerLongitude:[%s+TO+1000]'% (lat, lat, lon, lon))
    query = [aq_date, cloud, add]
    and_string = '+AND+'.join(map(str, query))
    r = requests.get('%s?search=%s&limit=%s' % (API_URL, and_string, limit))
    r_dict = json.loads(r.text)
    result = {}
    result['total'] = r_dict['meta']['found']
    result['limit'] = r_dict['meta']['limit']
    result['total_returned'] = len(r_dict['results'])
    result['results'] = [{'sceneID': i['sceneID'],
                          'sat_type': u'L8',
                          'path2': '%03d'%i['path'],
                          'row2': '%03d'%i['row'],
                          'download_links' : i['download_links'],
                          'BPF_NAME_OLI' : i['BPF_NAME_OLI'],
                          'thumbnail': i['browseURL'],
                          'date': i['acquisitionDate'],
                          'GROUND_CONTROL_POINTS_VERSION': i['GROUND_CONTROL_POINTS_VERSION'],
                          'DATE_L1_GENERATED': i['DATE_L1_GENERATED'],
                          'NADIR_OFFNADIR': i['NADIR_OFFNADIR'],
                          'data_geometry': i['data_geometry'],
                          'sunAzimuth': i['sunAzimuth'],
                          'cloudCover': i['cloudCover'],
                          'COLLECTION_NUMBER': i['COLLECTION_NUMBER'],
                          'sceneCenterLatitude': i['sceneCenterLatitude'],
                          'cartURL': i['cartURL'],
                          'sunElevation': i['sunElevation'],
                          'cloud_coverage': i['cloud_coverage'],
                          'CLOUD_COVER_LAND': i['CLOUD_COVER_LAND'],
                          'scene_id': i['scene_id'],
                          'GROUND_CONTROL_POINTS_MODEL': i['GROUND_CONTROL_POINTS_MODEL'],
                          'row': i['row'],
                          'imageQuality1': i['imageQuality1'],
                          'cloudCoverFull': i['cloudCoverFull'],
                          'aws_index': i['aws_index'],
                          'browseURL': i['browseURL'],
                          'browseAvailable': i['browseAvailable'],
                          'BPF_NAME_TIRS': i['BPF_NAME_TIRS'],
                          'dayOrNight': i['dayOrNight'],
                          'TIRS_SSM_MODEL': i['TIRS_SSM_MODEL'],
                          'CPF_NAME': i['CPF_NAME'],
                          'FULL_PARTIAL_SCENE': i['FULL_PARTIAL_SCENE'],
                          'DATA_TYPE_L1': i['DATA_TYPE_L1'],
                          'aws_thumbnail': i['aws_thumbnail'],
                          'google_index': i['google_index'],
                          'sceneStartTime': i['sceneStartTime'],
                          'dateUpdated': i['dateUpdated'],
                          'sensor': i['sensor'],
                          'lowerRightCornerLatitude': i['lowerRightCornerLatitude'],
                          'LANDSAT_PRODUCT_ID': i['LANDSAT_PRODUCT_ID'],
                          'acquisitionDate': i['acquisitionDate'],
                          'PROCESSING_SOFTWARE_VERSION': i['PROCESSING_SOFTWARE_VERSION'],
                          'lowerRightCornerLongitude': i['lowerRightCornerLongitude'],
                          'lowerLeftCornerLatitude': i['lowerLeftCornerLatitude'],
                          'sceneCenterLongitude': i['sceneCenterLongitude'],
                          'COLLECTION_CATEGORY': i['COLLECTION_CATEGORY'],
                          'upperLeftCornerLongitude': i['upperLeftCornerLongitude'],
                          'path': i['path'],
                          'lowerLeftCornerLongitude': i['lowerLeftCornerLongitude'],
                          'GEOMETRIC_RMSE_MODEL_X': i['GEOMETRIC_RMSE_MODEL_X'],
                          'GEOMETRIC_RMSE_MODEL_Y': i['GEOMETRIC_RMSE_MODEL_Y'],
                          'sceneStopTime': i['sceneStopTime'],
                          'upperLeftCornerLatitude': i['upperLeftCornerLatitude'],
                          'upperRightCornerLongitude': i['upperRightCornerLongitude'],
                          'product_id': i['product_id'],
                          'satellite_name': i['satellite_name'],
                          'GEOMETRIC_RMSE_MODEL': i['GEOMETRIC_RMSE_MODEL'],
                          'upperRightCornerLatitude': i['upperRightCornerLatitude'],
                          'receivingStation': i['receivingStation'],
                          'cloud': i['cloudCoverFull']} for i in r_dict['results']]
    return result


def get_wrs2(lat, lon):
    y_m_d = datetime(2015, 1,1)
    y_m_d_e = datetime(2018, 12,1)
    try:
        ret = que_land(lat=lat, lon=lon, start='%04d-%02d-%02d'%(y_m_d.year, y_m_d.month, y_m_d.day),\
                           end='%04d-%02d-%02d'%(y_m_d_e.year, y_m_d_e.month, y_m_d_e.day), maxc=10, minc=0, limit=1)
        return ret['results'][0]['path'], ret['results'][0]['row']
    except:
        print 'This place has no Landsat 8 measurements, please double check it with: https://earthexplorer.usgs.gov/ !'