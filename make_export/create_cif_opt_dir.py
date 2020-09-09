#!/usr/bin/env python
"""Utility to create a folder with opt_cif_ddec CIFs."""
import os
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group, CifData

from figure.config import load_profile
load_profile()

TAG_KEY = "tag4"
CIFS_DIR = "./cifs_cellopt/"

os.mkdir(CIFS_DIR)

qb = QueryBuilder()
qb.append(Group, project=['label'], filters={'label': {'like': r"curated-cof\_%"}}, tag='group')
qb.append(CifData, project=['*'], filters={'extras.{}'.format(TAG_KEY): 'opt_cif_ddec'}, with_group='group')
qb.order_by({CifData: {'label': 'asc'}})

for q in qb.all():
    mat_id = q[0].split("_")[1]
    ddec_cif = q[1]
    ddec_cif.label = mat_id + "_DDEC"
    filename = '{}_ddec.cif'.format(mat_id)
    cifile = open(os.path.join(CIFS_DIR, filename), 'w+')
    print(ddec_cif.get_content(), file=cifile)
    print("{},{}".format(mat_id, ddec_cif))
