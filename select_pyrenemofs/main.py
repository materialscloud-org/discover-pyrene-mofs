"""Provenance table"""

import panel as pn
from select_pyrenemofs.table import get_table


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


buttons = pn.Row()

buttons.append(fake_button(
    link="https://github.com/lsmo-epfl/discover-pyrene-mofs/blob/master/pipeline_pyrenemofs/static/pynene-mofs-info.csv", 
    label="Info CSV",
    button_type="primary")) # Link to GitHub file

buttons.append(fake_button(
    link="https://archive.materialscloud.org/deposit/records/file?file_id=cbd0a0f3-69ed-4ba0-8536-2f10cc1562a7&filename=CIF_files.zip",  
    label="Crystallographic Information Files",
    button_type="primary")) # Link to zip file in the Materials Cloud Archive

buttons.append(fake_button(
    link="figure_pyrenemofs", 
    label="Interactive Plot",
    button_type="primary"))

t = pn.Column()
t.append(buttons)
t.append(
    pn.pane.HTML(
        get_table().to_html(
            escape=False,  # keep html images
            classes='table table-striped table-hover'),
        style={
            'border': '3px solid black',
            'border-radius': '10px',
            'padding': '0px'
        }))

t.servable()
