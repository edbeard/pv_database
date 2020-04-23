import unittest

from pv_database.database import populate_metadata
from chemdataextractor import Document


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

            expected = {'authors': ['Monica Samal',
                 'Priyaranjan Mohapatra',
                 'Ramesh Subbiah',
                 'Chang-Lyoul Lee',
                 'Benayad Anass',
                 'Jang Ah Kim',
                 'Taesung Kim',
                 'Dong Kee Yi',
                 'Monica Samal',
                 'Priyaranjan Mohapatra',
                 'Ramesh Subbiah',
                 'Chang-Lyoul Lee',
                 'Benayad Anass',
                 'Jang Ah Kim',
                 'Taesung Kim',
                 'Dong Kee Yi'],
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