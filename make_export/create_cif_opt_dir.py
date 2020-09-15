#!/usr/bin/env python
"""Utility to create a folder with opt_cif_ddec CIFs."""

import os
import datetime
import pandas as pd
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group, CifData
from aiida.tools.importexport.dbexport import export  # Updated to AiiDA v1.3.0
from pipeline_pyrenemofs import TAG_KEY, GROUP_DIR

from aiida import load_profile
load_profile()

CIFS_DIR = "./cifs_cellopt/"
os.mkdir(CIFS_DIR)

mat_df = pd.read_csv('../pipeline_pyrenemofs/static/pynene-mofs-info.csv')
mat_list = list(mat_df['refcode'].values)

qb = QueryBuilder()
qb.append(CifData, filters={'label': {'in': mat_list}}, 
          tag='n', project='label')
qb.append(Group, with_node='n', filters={'label': {'like': GROUP_DIR + "%"}}, 
          tag='g')
qb.append(CifData, filters={'extras.{}'.format(TAG_KEY): 'opt_cif_ddec'}, with_group='g',
          project='*')
qb.order_by({CifData: {'label': 'asc'}})

for q in qb.all():
    mat_id = q[0]
    ddec_cif = q[1]
    ddec_cif.label = mat_id + "_DDEC"
    filename = '{}_ddec.cif'.format(mat_id)
    cifile = open(os.path.join(CIFS_DIR, filename), 'w+')
    print(ddec_cif.get_content(), file=cifile)
    print("{},{}".format(mat_id, ddec_cif))
