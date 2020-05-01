from pymongo import MongoClient
from mpi4py import MPI

from dsc_db import PhotovoltaicRecord, create_dsscdb_from_file
from chemdataextractor.doc import Table, Document
from chemdataextractor.doc import Caption

import os

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


def photovoltaic_record_to_database(pv_records, metadata, citations):
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
            'table_data': {}, # A dictionary of raw info from the table
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

        # Add citation data
        add_citation_data(pv_record, db_record, citations)

        # Add the data from the first column of each table
        db_record['table_data'] = add_table_metadata(pv_record)

        # pprint(db_record)
        db_records.append(db_record)

    return db_records


def add_citation_data(pv_record, db_record, citations):
    """
    Add the citation data to the db_records
    :param pv_record: Input photovoltaic record object
    :param db_record: Input db_record object
    :return:
    """

    ref_record = getattr(pv_record, 'ref', None)
    if ref_record is not None:
        if len(ref_record.keys()) > 1:
            raise Exception
        if 'value' in ref_record['Reference'].keys():
            ref_id = int(ref_record['Reference']['value'][0]) - 1
            if 0 < ref_id < len(citations):
                ref_record['Reference']['content'] = citations[ref_id].text

        db_record['device_reference'] = ref_record['Reference']

    return db_record


def populate_citations(doc):
    """
    Get the citation data from the document
    :param pv_record:
    :return:
    """

    # get the documents citation data
    return [citation.serialize() for citation in doc.citations]


def add_table_metadata(pv_record):
    """ Adding data from the first column of the table"""

    table_meta = {}

    row_category_data = {}
    row_categories = pv_record.table.tde_table.row_categories

    keys = list(row_categories.pre_cleaned_table[0])
    data = list(row_categories.pre_cleaned_table[1:])

    for d in data:
        datum = list(d)
        indicator = ' '.join(datum)
        if indicator == pv_record.table_row_categories:
            for i, key in enumerate(keys):
                row_category_data[key] = datum[i]

    table_meta['caption'] = pv_record.table.caption.text
    table_meta['first_columns'] = row_category_data

    return table_meta


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

    paper = '/home/edward/pv/extractions/input_filtered_tables/dsc/C3CS60449G.html'

    try:
        with open(paper, 'rb') as f:
            doc = Document.from_file(f)
    except Exception as e:
        print('the failed paper: %s' % paper)

    filename = os.path.splitext(os.path.basename(paper))[0]

    citations = populate_citations(doc)

    # Step 2: Obtain the PV records
    pv_records = create_dsscdb_from_file(doc)

    # Step 3: When records found, get the metadata
    if pv_records:
        metadata = populate_metadata(doc)

        # Step 4: Convert to JSON
        output_dict = photovoltaic_record_to_database(pv_records, metadata, citations)
        pprint(output_dict)




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
