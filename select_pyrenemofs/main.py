"""Provenance table"""

import panel as pn
from select_pyrenemofs.table import get_table


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


buttons = pn.Row()
buttons.append(fake_button(link="pipeline_config/static/pyrene-mofs-info.csv", label="Info CSV",
                           button_type="primary"))  #audoderect to the GitHub file!
buttons.append(
    fake_button(
        link="https://archive.materialscloud.org/file/2019.0034/v2/cifs_cellopt_Dec19.zip",  #make an archive
        label="Crystallographic Information Files",
        button_type="primary"))
buttons.append(fake_button(
    link="figure_pyrenemofs",  #make an archive
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
