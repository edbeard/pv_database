"""
Create the perovskite database in the correct format
"""
from pv_database.database import device_characteristics, device_metrology, add_citation_data, add_table_metadata, \
    populate_citations, populate_metadata
from dsc_db.run_perovskites import create_pdb_from_file

import os
from pprint import pprint
import json
from chemdataextractor.doc import Document


psc_material_components = [
    'perovskite', 'substrate', 'etl', 'htl', 'counter_electrode'
]

psc_material_metrology = [
    'charge_transfer_resistance', 'series_resistance'
]

all_properties = {
    'device_characteristics': device_characteristics,
    'dsc_material_components': psc_material_components,
    'device_metrology': device_metrology,
    'dsc_material_metrology': psc_material_metrology,
}


def perovskite_record_to_database(pv_records, metadata, citations):
    """
    Converts the perovskite record to the correct database format
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
            'device_reference': {}, # A dictionary of the reference number, and the data of the citation
            'article_info': metadata
        }

        # Device characteristics
        for category, fields in all_properties.items():
            for field in fields:
                field_record = getattr(pv_record, field, None)
                if field_record is not None:
                    if len(field_record.keys()) > 1:
                        raise Exception

                    data = next(iter(field_record.values()))
                    db_record[category][field] = data

        # Add citation data
        db_record['device_reference'] = add_citation_data(pv_record, citations)

        # Add the data from the first column of each table
        db_record['table_data'] = add_table_metadata(pv_record)

        # pprint(db_record)
        db_records.append(db_record)

    return db_records


if __name__ == '__main__':
    paper = '/home/edward/pv/extractions/psc_fscore_eval/input_filtered_tables/psc/10.1016:j.cplett.2017.12.012.xml'

    try:
        with open(paper, 'rb') as f:
            doc = Document.from_file(f)
    except Exception as e:
        print('the failed paper: %s' % paper)

    filename = os.path.splitext(os.path.basename(paper))[0]

    citations = populate_citations(doc)

    # Step 2: Obtain the PV records
    pv_records = create_pdb_from_file(doc)

    # Step 3: When records found, get the metadata
    if pv_records:
        metadata = populate_metadata(doc)

        # Step 4: Convert to JSON
        output_dict = perovskite_record_to_database(pv_records, metadata, citations)
        pprint(output_dict)

        with open('../debug.json', 'w') as outf:
            json.dump(output_dict, outf)
    else:
        print('No records found.')
