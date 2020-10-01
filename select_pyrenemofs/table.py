"""Provenance table"""

import re
from functools import lru_cache
from pipeline_pyrenemofs import get_db_nodes_dict, get_pyrene_mofs_df, load_profile
load_profile()

AIIDA_LOGO_URL = "select_pyrenemofs/static/images/aiida-128.png"
DOI_LOGO_URL = 'select_pyrenemofs/static/images/paper-128.png'
MAT_LOGO_URL = 'select_pyrenemofs/static/images/mat-128.png'


def doi_link(mat_dict):
    """Return the DOI link of the article."""
    doi = mat_dict['orig_cif'].extras['doi_ref']
    return "<a href='https://doi.org/{}' target='_blank'><img class='provenance-logo' src='{}'></a>".format(
        doi, DOI_LOGO_URL)


def detail_link(mat_id):
    """Return representation of workflow link."""
    return "<a href='detail_pyrenemofs?mat_id={}' target='_blank'><img class='provenance-logo' src='{}'></a>".format(
        mat_id, MAT_LOGO_URL)


@lru_cache()
def get_elements_from_cifdata(cifdata):
    formula = cifdata.get_ase().get_chemical_formula()
    elements = [e for e in re.split(r'\d+', formula) if e]
    return ",".join(elements)


@lru_cache(maxsize=1)
def get_table():
    """Get the entries for the right table of select-figure."""
    import pandas as pd

    pd.set_option('max_colwidth', 10)

    df_info = get_pyrene_mofs_df()
    df_tabl = pd.DataFrame(columns=[  # Set the order of the columns
        'Name', 'Article', 'Elements', 'Surface (m2/g)', 'Structure'
    ])

    db_nodes_dict = get_db_nodes_dict()

    for _i, df_info_row in df_info.iterrows():
        mat_id = df_info_row['refcode']
        mat_dict = db_nodes_dict[mat_id]
        #mat_dict['orig_cif'].set_extra('name_conventional', df_info_row['name']) # Used to correct materials' info!
        new_row = {
            'Order': df_info_row['idx'],
            'Name': mat_dict['orig_cif'].extras['name_conventional'],
            'Article': doi_link(mat_dict),
            'Elements': df_info_row['elements'],  #not working bad cif: get_elements_from_cifdata(mat_dict['orig_cif']),
            'Structure': detail_link(mat_id),
            'Ligand': df_info_row['ligand']
        }

        if 'opt_zeopp' in mat_dict:
            new_row['Surface (m2/g)'] = int(mat_dict['opt_zeopp']['ASA_m^2/g'])
        else:
            new_row['Surface (m2/g)'] = int(mat_dict['orig_zeopp']['ASA_m^2/g'])

        df_tabl = df_tabl.append(new_row, ignore_index=True)

    df_tabl = df_tabl.sort_values(by=['Order'])
    df_tabl = df_tabl.drop(columns=['Order'])
    df_tabl = df_tabl.reset_index(drop=True)
    df_tabl.index += 1
    return df_tabl
