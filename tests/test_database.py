import unittest

from pv_database.database import populate_metadata, add_table_metadata, add_citation_data
from chemdataextractor import Document
from chemdataextractor.doc.table import Table
from chemdataextractor.doc import Caption, Citation
from dsc_db import PhotovoltaicRecord


class TestDatabase(unittest.TestCase):

    def test_populate_metadata_elsevier(self):

        path_to_doc = '/home/edward/pv/extractions/input/10.1016:j.orgel.2019.105395.xml'
        with open(path_to_doc, 'rb') as f:
            doc = Document.from_file(f)

        metadata = populate_metadata(doc)

        expected = {'authors': ['Yi Di',
                     'Suping Jia',
                     'Ning Li',
                     'Caihong Hao',
                     'Huinian Zhang',
                     'Shengliang Hu'],
             'date': '2019-08-03',
             'doi': '10.1016/j.orgel.2019.105395',
             'firstpage': '105395',
             'html_url': 'https://sciencedirect.com/science/article/pii/S1566119919304148',
             'issue': '1566-1199',
             'journal': 'Organic Electronics',
             'language': None,
             'lastpage': None,
             'pdf_url': None,
             'publisher': '© 2019 Elsevier B.V. All rights reserved.',
             'title': 'Ni-incorporated carbon materials derived from humic acid as '
                      'efficient low-cost electrocatalysts for dye-sensitized solar cells',
             'volume': '76'}

        self.assertEqual(metadata, expected)

    def test_populate_metadata_rsc(self):

        path_to_doc = '/home/edward/pv/extractions/input/C3NR02333H.html'
        with open(path_to_doc, 'rb') as f:
            doc = Document.from_file(f)

            expected = {'authors': ['Monica\xa0Samal',
             'Priyaranjan\xa0Mohapatra',
             'Ramesh\xa0Subbiah',
             'Chang-Lyoul\xa0Lee',
             'Benayad\xa0Anass',
             'Jang Ah\xa0Kim',
             'Taesung\xa0Kim',
             'Dong Kee\xa0Yi',
             'Monica\xa0Samal',
             'Priyaranjan\xa0Mohapatra',
             'Ramesh\xa0Subbiah',
             'Chang-Lyoul\xa0Lee',
             'Benayad\xa0Anass',
             'Jang Ah\xa0Kim',
             'Taesung\xa0Kim',
             'Dong Kee\xa0Yi'],
             'date': '2013/09/26',
             'doi': '10.1039/C3NR02333H',
             'firstpage': '9793',
             'html_url': 'https://pubs.rsc.org/en/content/articlelanding/2013/nr/c3nr02333h',
             'issue': '20',
             'journal': 'Nanoscale',
             'language': 'en',
             'lastpage': '9805',
             'pdf_url': 'https://pubs.rsc.org/en/content/articlepdf/2013/nr/c3nr02333h',
             'publisher': 'Royal Society of Chemistry',
             'title': 'InP/ZnS–graphene oxide and reduced graphene oxide nanocomposites as '
                      'fascinating materials for potential optoelectronic applications  ',
             'volume': '5'}

        metadata = populate_metadata(doc)
        self.assertEqual(metadata, expected)

    def test_add_first_column(self):

        table_input = [['CE',	'Jsc (mA cm−2)', 'Voc (V)', 'FF', 'PCE'], ['Pt', '11.11', '22.22', '33.33', '44.44'],
                       ['Ag', '11.11', '22.22', '33.33', '44.44']]
        table = Table(caption=Caption('Null'), table_data=table_input)

        input = {
            'voc': {'OpenCircuitVoltage': {'raw_units': '(mV)', 'raw_value': '756', 'specifier': 'Voc',
                                       'units': '(10^-3.0) * Volt^(1.0)', 'value': [756.0]}},
            'table_row_categories': 'Pt'
        }
        pv_record = PhotovoltaicRecord(input, table)
        table_meta = add_table_metadata(pv_record)
        expected = {'caption': 'Null', 'first_columns': {'CE': 'Pt'}}
        self.assertEqual(table_meta, expected)

    def test_add_first_column_2(self):
        table_input = [['Dye',	'Electrolyte', 'Voc (V)', 'FF', 'PCE'], ['NT35', 'Iodine', '22.22', '33.33', '44.44'],
                       ['', 'Cobalt', '22.22', '33.33', '44.44'], ['G221', 'Iodine', '22.22', '33.33', '44.44'],
                       ['G221', 'Cobalt', '22.22', '33.33', '44.44']]
        table = Table(caption=Caption('This is the caption'), table_data=table_input)


        input = {'dye': {'Dye': [{'compound': {'labels': ['G221'],
                               'names': ['(E)-3-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)-2-cyanoacrylic '
                                         'acid',
                                         '(E)-3-(4-(Bis(4-(hexyloxy)phenyl)amino)phenyl)-2-cyano '
                                         'acrylic acid'],
                               'roles': ['product']},
                                  'raw_value': 'G221',
                                  'specifier': 'Dye'}]},
                 'electrolyte': {'Electrolyte': {'raw_value': 'Cobalt',
                                                 'specifier': 'Electrolyte'}},
                 'ff': {'FillFactor': {'raw_value': '0.765',
                                       'specifier': 'FF',
                                       'value': [0.765]}},
                 'pce': {'PowerConversionEfficiency': {'raw_units': '(%)',
                                                       'raw_value': '3.62',
                                                       'specifier': 'η',
                                                       'units': 'Percent^(1.0)',
                                                       'value': [3.62]}},
                 'table_row_categories': 'G221 Cobalt',
                 'voc': {'OpenCircuitVoltage': {'raw_units': '(mV)',
                                                'raw_value': '721',
                                                'specifier': 'Voc',
                                                'units': '(10^-3.0) * Volt^(1.0)',
                                                'value': [721.0]}}}

        pv_record = PhotovoltaicRecord(input, table)
        table_meta = add_table_metadata(pv_record)
        self.assertEqual(table_meta, {'caption': 'This is the caption', 'first_columns': {'Dye': 'G221', 'Electrolyte': 'Cobalt'}})

    def test_add_citations(self):
        citations = [Citation('This is not the right citation'), Citation('D. D. Eley, Nature, 1948, 162, 819\xa0CrossRefCAS')]
        table = Table(Caption('Dummy table'))


        input = {'dye': {'Dye': [{'compound': {'labels': ['G221'],
                               'names': ['(E)-3-(4-(bis(4-(hexyloxy)phenyl)amino)phenyl)-2-cyanoacrylic '
                                         'acid',
                                         '(E)-3-(4-(Bis(4-(hexyloxy)phenyl)amino)phenyl)-2-cyano '
                                         'acrylic acid'],
                               'roles': ['product']},
                                  'raw_value': 'G221',
                                  'specifier': 'Dye'}]},
                 'electrolyte': {'Electrolyte': {'raw_value': 'Cobalt',
                                                 'specifier': 'Electrolyte'}},
                 'ff': {'FillFactor': {'raw_value': '0.765',
                                       'specifier': 'FF',
                                       'value': [0.765]}},
                 'pce': {'PowerConversionEfficiency': {'raw_units': '(%)',
                                                       'raw_value': '3.62',
                                                       'specifier': 'η',
                                                       'units': 'Percent^(1.0)',
                                                       'value': [3.62]}},
                 'ref': {'Reference': {
                     'value': [2.0],
                     'raw_value': '2',
                     'specifier': 'Ref.'
                         }},
                 'table_row_categories': 'G221 Cobalt',
                 'voc': {'OpenCircuitVoltage': {'raw_units': '(mV)',
                                                'raw_value': '721',
                                                'specifier': 'Voc',
                                                'units': '(10^-3.0) * Volt^(1.0)',
                                                'value': [721.0]}}}

        pv_record = PhotovoltaicRecord(input, table)
        db_record = add_citation_data(pv_record, {}, citations)
        expected = {'device_reference': {'value': [2.0], 'raw_value': '2', 'specifier': 'Ref.', 'content': 'D. D. Eley, Nature, 1948, 162, 819\xa0CrossRefCAS'}}
        self.assertEqual(db_record, expected)
