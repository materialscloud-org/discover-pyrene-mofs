#!/usr/bin/env python
"""Utility to create the export for www.materialscloud.org/discover/curated-cofs.
Since September 2020 it includes two types of groups:
* discover_curated_cofs/05001N2 "ccs_groups" with only selected data for co2 capture and sequestration (ccs), for legacy
* curated-cof_05001N2_v1 "full_groups" with all data
"""

import sys
import datetime
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group
from aiida.tools.importexport.dbexport import export  # Updated to AiiDA v1.3.0

from figure.config import load_profile
load_profile()

TAG_KEY = "tag4"
CSS_GROUP_DIR = "discover_curated_cofs/"
EXPORT_FILE_NAME = "export_discovery_cof_{}.aiida".format(datetime.date.today().strftime(r'%d%b%y'))

EXPORT = True
PRINT_OPT_CIFS = False
CLEAR = False

css_nodes = ['orig_cif', 'orig_zeopp', 'dftopt', 'opt_cif_ddec', 'opt_zeopp', 'isot_co2', 'isot_n2', 'appl_pecoal']


def delete_css_groups():
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': CSS_GROUP_DIR + "%"}})
    if qb.all():
        print("Groups '{}' found, deleting...".format(CSS_GROUP_DIR))
        for q in qb.all():
            group = q[0]
            group.clear()
            Group.objects.delete(group.pk)
    else:
        print("No previous Group {} found to delete.".format(CSS_GROUP_DIR))


# Clear and delete CSS groups created in a previous session
delete_css_groups()

# Query for all the CURATED-COFs
qb = QueryBuilder()
qb.append(Group, filters={'label': {'like': r'curated-cof\_%\_v%'}})
all_full_groups = qb.all(flat=True)  #

# Create groups for each and fill them with CSS nodes
print("Creating CCS-groups, with tagged nodes:", css_nodes)

all_css_groups = []
for full_group in all_full_groups:
    mat_id = full_group.label.split("_")[1]
    css_group = Group(label=CSS_GROUP_DIR + mat_id).store()
    all_css_groups.append(css_group)
    left_nodes = css_nodes.copy()
    for node in full_group.nodes:
        if TAG_KEY not in node.extras:
            sys.exit("WARNING: node <{}> has no extra '{}'".format(node.id, TAG_KEY))
        if node.extras[TAG_KEY] in left_nodes:
            css_group.add_nodes(node)
            left_nodes.remove(node.extras[TAG_KEY])
    print(mat_id, "missing nodes for CSS: ", left_nodes)

# Export these groups
if EXPORT:
    print(" ++++++ Exporting Nodes ++++++ ")
    kwargs = {
        # general
        'entities': all_full_groups + all_css_groups,
        'filename': EXPORT_FILE_NAME,
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

# Delete new groups after the export
if CLEAR:
    delete_css_groups()
