# coding: utf-8
import panel as pn
import param
from collections import OrderedDict
import bokeh.models as bmd
import bokeh.plotting as bpl
from bokeh.palettes import Plasma256
from pipeline_pyrenemofs import get_db_nodes_dict, get_figure_values
from pipeline_pyrenemofs import quantities

from aiida import load_profile
load_profile()

def update_legends(p, q_list, hover):
    hover.tooltips = [
        ("COF ID", "@mat_id"),
        (q_list[0]["label"], "@x {}".format(q_list[0]["unit"])),
        (q_list[1]["label"], "@y {}".format(q_list[1]["unit"])),
        (q_list[2]["label"], "@color {}".format(q_list[2]["unit"])),
    ]

    p.xaxis.axis_label = "{} [{}]".format(q_list[0]["label"], q_list[0]["unit"])
    p.yaxis.axis_label = "{} [{}]".format(q_list[1]["label"], q_list[1]["unit"])
    p.title.text = "{} [{}]".format(q_list[2]["label"], q_list[2]["unit"])


def get_plot(inp_x, inp_y, inp_clr):
    """Returns a Bokeh plot of the input values, and a message with the number of COFs found."""
    q_list = [quantities[label] for label in [inp_x, inp_y, inp_clr]]
    db_nodes_dict = get_db_nodes_dict() # TODO: try to move outside, to load it once!
    results = get_figure_values(db_nodes_dict,q_list)  #returns [inp_x_value, inp_y_value, inp_clr_value, cif.label]

    # prepare data for plotting
    nresults = len(results)
    msg = "{} MOFs found.<br> <b>Click on any point for details!</b>".format(nresults)

    label, x, y, clrs = zip(*results)
    x = list(map(float, x))
    y = list(map(float, y))
    clrs = list(map(float, clrs))
    mat_id = label

    data = {'x': x, 'y': y, 'color': clrs, 'mat_id': mat_id}

    # create bokeh plot
    source = bmd.ColumnDataSource(data=data)

    hover = bmd.HoverTool(tooltips=[])
    tap = bmd.TapTool()
    p_new = bpl.figure(
        plot_height=600,
        plot_width=600,
        toolbar_location='above',
        tools=[
            'pan',
            'wheel_zoom',
            'box_zoom',
            'save',
            'reset',
            hover,
            tap,
        ],
        active_drag='box_zoom',
        output_backend='webgl',
        title='',  # trick: title is used as the colorbar label
        title_location='right',
        x_axis_type=q_list[0]['scale'],
        y_axis_type=q_list[1]['scale'],
    )
    p_new.title.align = 'center'
    p_new.title.text_font_size = '10pt'
    p_new.title.text_font_style = 'italic'
    update_legends(p_new, q_list, hover)
    tap.callback = bmd.OpenURL(url="detail_pyrenemofs?mat_id=@mat_id")

    cmap = bmd.LinearColorMapper(palette=Plasma256, low=min(clrs), high=max(clrs))
    fill_color = {'field': 'color', 'transform': cmap}
    p_new.circle('x', 'y', size=10, source=source, fill_color=fill_color)
    cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
    p_new.add_layout(cbar, 'right')

    return p_new, msg


pn.extension()

class StructurePropertyVisualizer(param.Parameterized):

    x = param.Selector(objects=quantities.keys(), default='Largest Included Sphere Diameter')
    y = param.Selector(objects=quantities.keys(), default='Geometric Void Fraction')
    color = param.Selector(objects=quantities.keys(), default='Density')
    msg = pn.pane.HTML("")
    _plot = None  # reference to current plot

    @param.depends('x', 'y', 'color')
    def plot(self):
        selected = [self.x, self.y, self.color]
        unique = set(selected)
        if len(unique) < len(selected):
            self.msg.object = "<b style='color:red;'>Warning: you are asking to show the same value twice!</b>"
            return self._plot

        self._plot, self.msg.object = get_plot(self.x, self.y, self.color)
        return self._plot


explorer = StructurePropertyVisualizer()

gspec = pn.GridSpec(sizing_mode='stretch_both', max_width=1000, max_height=300)
gspec[0, 0] = explorer.param
gspec[:2, 1:4] = explorer.plot
gspec[1, 0] = explorer.msg

gspec.servable()
