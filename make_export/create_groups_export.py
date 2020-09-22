#!/usr/bin/env python
"""Utility to create the export for www.materialscloud.org/discover/pyrene-mofs.
"""

import sys
import datetime
import pandas as pd
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group, CifData
from aiida.tools.importexport.dbexport import export  # Updated to AiiDA v1.3.0
from pipeline_pyrenemofs import TAG_KEY, GROUP_DIR

from pipeline_pyrenemofs import load_profile
load_profile()

mat_df = pd.read_csv('../pipeline_pyrenemofs/static/pynene-mofs-info.csv')
mat_list = list(mat_df['refcode'].values)

qb = QueryBuilder()
qb.append(CifData, filters={'label': {'in': mat_list}}, tag='n')
qb.append(Group, with_node='n', filters={'label': {'like': GROUP_DIR + "%"}}, tag='g', project='*')


kwargs = {
    # general
    'entities': qb.all(flat=True),
    'filename': "export_pyrene_mofs_{}.aiida".format(datetime.date.today().strftime(r'%d%b%y')),
    'overwrite': True,
    'silent': False,
    'use_compression': True,
    # trasversal rules
    'input_calc_forward': False,  #cli default: False
    'input_work_forward': False,  #cli default: False
    'create_backward': True,  #cli default: True
    'return_backward': True,  #cli default: False
    'call_calc_backward': True,  #cli default: False
    'call_work_backward': True,  #cli default: False
    # include
    'include_comments': True,  #cli default: True
    'include_logs': True,  #cli default: True
}
export(**kwargs)

