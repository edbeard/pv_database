from pymongo import MongoClient
from mpi4py import MPI

from dsc_db import PhotovoltaicRecord
from chemdataextractor.doc import Table
from chemdataextractor.doc import Caption

from pprint import pprint

# from dsc_db.run import create_dsscdb_from_file
# from dsc_db.model import PhotovoltaicRecord

# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()

# Defining the different fields

# voc = ModelType(OpenCircuitVoltage, required=False, contextual=False)
# ff = ModelType(FillFactor, required=False, contextual=False)
# pce = ModelType(PowerConversionEfficiency, required=False, contextual=False)
# jsc = ModelType(ShortCircuitCurrentDensity, required=False, contextual=False)
# dye = ModelType(Dye, required=False, contextual=False)
# ref = ModelType(Reference, required=False, contextual=False)
# redox_couple = ModelType(RedoxCouple, required=False, contextual=False)
# dye_loading = ModelType(DyeLoading, required=False, contextual=False)
# counter_electrode = ModelType(CounterElectrode, required=False, contextual=False)
# semiconductor = ModelType(Semiconductor, required=False, contextual=False)
# active_area = ModelType(ActiveArea, required=False, contextual=False)
# solar_simulator = ModelType(SimulatedSolarLightIntensity, required=False, contextual=True)
# electrolyte = ModelType(Electrolyte, required=False, contextual=False)
# substrate = ModelType(Substrate, required=False, contextual=False)
# charge_transfer_resisitance = ModelType(ChargeTransferResistance, required=False, contextual=False)
# series_resisitance = ModelType(SeriesResistance, required=False, contextual=False)
# exposure_time = ModelType(ExposureTime, required=False, contextual=True)

device_characteristics = [
    'voc', 'jsc', 'ff', 'pce'#, 'p_in', 'p_max'
]

dsc_material_components = [
    'dye', 'substrate', 'semiconductor', 'redox_couple', 'counter_electrode', 'electrolyte'
]

device_metrology = [
    'solar_simulator', 'active_area', 'exposure_time'
]

dsc_material_metrology = [
    'dye_loading', 'charge_transfer_resisitance', 'series_resisitance'
]

all_properties = {
    'device_characteristics': device_characteristics,
    'dsc_material_components': dsc_material_components,
    'device_metrology': device_metrology,
    'dsc_material_metrology': dsc_material_metrology,
}


def populate_metadata(doc):
    """
    Creates the metadata dictionary from document
    :param doc:
    :return:
    """

    metadata = doc.metadata
    if len(metadata) == 2:
        # Merge these cases from Elsevier where 2 metadata locations were used
        dict1 = metadata[0].data
        dict2 = metadata[1].data
        meta_dict = {**dict1, **dict2}
    else:
        meta_dict = metadata[0].data

    #pprint(meta_dict)
    return meta_dict


def photovoltaic_record_to_database(pv_records, metadata):
    """
    Converts the photovoltaic record to the correct database format
    :param pv_records: List of PhotovoltaicRecord objects to be converted
    :return: output: Dictionary in correct formatting
    """

    # Initialize the record
    db_records = []

    # Populate fields according to the above values
    for pv_record in pv_records:

        db_record = {
            'device_characteristics': {},
            'dsc_material_components': {},
            'device_metrology': {},
            'dsc_material_metrology': {},
            'device_reference': [],
            'article_info': metadata
        }

        # Device characteristsics
        for category, fields in all_properties.items():
            for field in fields:
                field_record = getattr(pv_record, field, None)
                if field_record is not None:
                    if len(field_record.keys()) > 1:
                        raise Exception

                    data = next(iter(field_record.values()))
                    db_record[category][field] = data


        # Add reference data
        ref_record = getattr(pv_record, 'ref', None)
        if ref_record and field_record is not None:
            if len(field_record.keys()) > 1:
                raise Exception
            db_record['device_reference'] = ref_record

        # pprint(db_record)
        db_records.append(db_record)

    return db_records


if __name__ == '__main__':

    practice_records = [
        PhotovoltaicRecord({'dye': {'Dye': [{'abbreviations': [['hierarchically',
                                         'structured',
                                         'multi-layer']],
                      'raw_value': 'HSM',
                      'specifier': 'Sample'}]},
        'ff': {'FillFactor': {'raw_value': '68.7',
                           'specifier': 'FF',
                           'value': [68.7]}},
        'jsc': {'ShortCircuitCurrentDensity': {'raw_units': '(mAcm−2)',
                                            'raw_value': '20.3',
                                            'specifier': 'Jsc',
                                            'units': '(10^1.0) * Ampere^(1.0)  '
                                                     'Meter^(-2.0)',
                                            'value': [20.3]}},
        'pce': {'PowerConversionEfficiency': {'raw_units': '(%)',
                                           'raw_value': '11.43',
                                           'specifier': 'η',
                                           'units': 'Percent^(1.0)',
                                           'value': [11.43]}},
        'voc': {'OpenCircuitVoltage': {'raw_units': '(mV)',
                                    'raw_value': '819.6',
                                    'specifier': 'Voc',
                                    'units': '(10^-3.0) * Volt^(1.0)',
                                    'value': [819.6]}}}, Table(Caption(''))),

        PhotovoltaicRecord({'dye': {'Dye': [{'abbreviations': [['hierarchically',
                                     'structured',
                                     'multi-layer']],
                  'raw_value': 'HSM',
                  'specifier': 'Sample'}]},
        'ff': {'FillFactor': {'raw_value': '77.8',
                       'specifier': 'FF',
                       'value': [77.8]}},
        'jsc': {'ShortCircuitCurrentDensity': {'raw_units': '(mAcm−2)',
                                        'raw_value': '2.7',
                                        'specifier': 'Jsc',
                                        'units': '(10^1.0) * Ampere^(1.0)  '
                                                 'Meter^(-2.0)',
                                        'value': [2.7]}},
        'pce': {'PowerConversionEfficiency': {'raw_units': '(%)',
                                       'raw_value': '12.16',
                                       'specifier': 'η',
                                       'units': 'Percent^(1.0)',
                                       'value': [12.16]}},
        'voc': {'OpenCircuitVoltage': {'raw_units': '(mV)',
                                'raw_value': '723.3',
                                'specifier': 'Voc',
                                'units': '(10^-3.0) * Volt^(1.0)'}}}, Table(Caption('')))
       ]

    photovoltaic_record_to_database(practice_records, None)



def run_parallel():

    """ Ruin the dssc_db script in parallel env."""

    if rank == 0:
        print('This doi is: %s, rank: %s' % (rank, doi))


# class DscDatabase():
#     """ Creates a property database of DSC devices  """
#
#     def __init__(self, collection='dsc', host, port):
#
#
#         self.client = MongoClient(host, port)
#
#
# class DscDatbaseEntry(dsc_database):
#
#     def populate_database(self):
#
#         # Step 1:
