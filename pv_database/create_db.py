"""
Create the database
"""

from mpi4py import MPI
import os
import json
import sys

from pv_database.database import populate_metadata, photovoltaic_record_to_database, populate_citations
from dsc_db import create_dsscdb_from_file
from dsc_db.model import PhotovoltaicRecord
from chemdataextractor import Document
from chemdataextractor.doc import Caption
from chemdataextractor.doc.table import Table


root_dir = '/projects/SolarWindowsADSP/ebeard/pv_database/input'
output_dir = '/projects/SolarWindowsADSP/ebeard/pv_database/output'
processed_input_dir = '/projects/SolarWindowsADSP/ebeard/pv_database/processed_input'


def create_db(host, port, db_name):
    # MPI parallel details
    comm = MPI.COMM_WORLD
    ranks = comm.size
    myrank = comm.rank

    if myrank == 0:
        print('Number of ranks: %s' % str(ranks))

    # Create a pool of papers
    list_of_papers = [os.path.join(root_dir, paper) for paper in os.listdir(root_dir)]
    if myrank == 0:
        print('number of papers found: %s' % len(list_of_papers))

    # End condition when no papers can be found by the algorithm
    if not list_of_papers:
        print('No papers found in input directory. Terminating.')
        sys.exit(0)

    # Extract papers
    for i, paper in enumerate(list_of_papers):

        if i % ranks == myrank:
            print('This paper is: %s on rank: %s' % (os.path.basename(paper), myrank))

            # Step 1: Load the document as CDE object
            try:
                with open(paper, 'rb') as f:
                    doc = Document.from_file(f)
            except Exception as e:
                print('the failed paper: %s' % paper)

            filename = os.path.splitext(os.path.basename(paper))[0]

            # Steb 1b - obtain the document citations
            citations = populate_citations(doc)

            # Step 2: Obtain the PV records
            pv_records = create_dsscdb_from_file(doc)

            # Step 3: When records found, get the metadata
            if pv_records:
                metadata = populate_metadata(doc)

                # Step 4: Convert to JSON
                output_dict = photovoltaic_record_to_database(pv_records, metadata, citations)

                output_path = os.path.join(output_dir, filename + '.json')
                with open(output_path, 'w') as outf:
                    json.dump(output_dict, outf)

            # Move the input paper to the processed_input directory
            os.rename(paper, os.path.join(processed_input_dir, os.path.basename(paper)))

if __name__ == '__main__':
    create_db('', '', 'dsc_db')
