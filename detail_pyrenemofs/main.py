#!/usr/bin/env python

import panel as pn
import pandas as pd

from detail_pyrenemofs.dft_info import plot_energy_steps
from detail_pyrenemofs.structure import structure_jsmol
from detail_pyrenemofs.utils import get_mat_id, get_details_title, get_geom_table, get_title
from pipeline_pyrenemofs import get_mat_nodes_dict

from pipeline_pyrenemofs import load_profile
load_profile()

pn.extension(css_files=['detail_pyrenemofs/static/style.css'])

class DetailView():

    def __init__(self):
        self.mat_id = get_mat_id()
        self.mat_nodes_dict = get_mat_nodes_dict(self.mat_id)
        print(">> Display details of MAT_ID:", self.mat_id, self.mat_nodes_dict['orig_cif'])

    @property
    def title_col(self):
        col = pn.Column(width=700)
        col.append(pn.pane.Markdown(get_details_title(self.mat_nodes_dict['orig_cif'])))
        return col

    @property
    def structure_col(self):
        nodes = self.mat_nodes_dict
        col = pn.Column(sizing_mode='stretch_width')
        if 'opt_cif_ddec' in nodes:
            col.append(get_title('Cell optimized structure', uuid=nodes['opt_cif_ddec'].uuid))
            col.append(pn.pane.Bokeh(structure_jsmol(nodes['opt_cif_ddec'])))
            col.append(get_title('Geometric properties', uuid=nodes["opt_zeopp"].uuid))
            col.append(pn.pane.Markdown(get_geom_table(nodes["opt_zeopp"])))
            col.append(get_title('Energy profile during cell optimization', uuid=nodes['dftopt'].uuid))
            col.append(pn.pane.Bokeh(plot_energy_steps(dftopt_out=nodes['dftopt'])))
        else:
            col.append(get_title('Cell structure (not DFT optimized)', uuid=nodes['orig_cif'].uuid))
            col.append(pn.pane.Bokeh(structure_jsmol(nodes['orig_cif'])))
            col.append(pn.pane.Markdown("""
            ###NOTE: 
            This MOF was not optimized because the framework is charged or DFT failed.
            """))
            col.append(get_title('Geometric properties (cell not optimized)', uuid=nodes["orig_zeopp"].uuid))
            col.append(pn.pane.Markdown(get_geom_table(nodes["orig_zeopp"])))
        return col

dv = DetailView()

page = dv.title_col
page.append(dv.structure_col)
page.servable()
