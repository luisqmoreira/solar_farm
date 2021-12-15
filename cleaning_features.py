import georasters as gr
import pandas as pd

def extract_tif(tif, name):
    """

    :param tif: Path for Tiff file
    :param name: Name you want to assign to variable
    :return: variable containing pandas DataFrame
    """

    col_name = name
    name = gr.from_file(tif)
    name = name.to_pandas()

    name.drop(['row', 'col'], axis=1, inplace=True)
    name = name[['x', 'y', 'value']]
    name.columns = ['long', 'lat', col_name]

    return name


def filter_loc(var):
    """

    :param var: Dataframe
    :return: filtered locations for Portugal
    """

    var = var[(var['long'] <= -6.0023606557377045) & (var['long'] >= -9.692065573770492) & (
            var['lat'] <= 43.999) & (var['lat'] >= 36.17707349468713)]
    var.reset_index(inplace=True)

    return var


"""
Convert Tiff file to pandas
"""

OPTA = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas'
                   '-v2_GEOTIFF/OPTA.tif', 'OPTA')

Temperature = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas'
                          '-v2_GEOTIFF/TEMP.tif', 'Temperature')

DIF = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF'
                  '/DIF.tif', 'DIF')

DNI = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF'
                  '/DNI.tif', 'DNI')

GHI = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF'
                  '/GHI.tif', 'GHI')

GTI = extract_tif('/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas'
                  '-v2_GEOTIFF/GTI.tif', 'GTI')

"""
Filter the dataframe for portuguese coordinates
"""

OPTA = filter_loc(OPTA)

Temperature = filter_loc(Temperature)

DIF = filter_loc(DIF)

DNI = filter_loc(DNI)

GHI = filter_loc(GHI)

GTI = filter_loc(GTI)

"""
Output dataframes to csv
"""

OPTA.to_csv('opta.csv')
Temperature.to_csv('temp.csv')
DIF.to_csv('dif.csv')
DNI.to_csv('dni.csv')
GHI.to_csv('ghi.csv')
GTI.to_csv('gti.csv')