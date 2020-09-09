from bokeh.plotting import figure
import bokeh.models as bmd


def get_startindex(steps):
    '''Take a list of steps and decide starting indices (and final number of steps).'''
    start_indices = []
    for i, step in enumerate(steps):
        if i == 0:
            start_indices.append(0)
        else:
            if step <= steps[i - 1]:
                start_indices.append(i)
    start_indices.append(len(steps))
    return start_indices


def plot_energy_steps(dftopt_out):  #pylint: disable=too-many-locals
    """Plot the total energy graph."""

    units = 'eV'
    ha2u = {'eV': 27.211399}

    out_dict = dftopt_out.get_dict()

    tooltips = [("Step (total)", "@index"), ("Step (stage)", "@step"), ("Energy", "@energy eV/atom"),
                ("Energy (dispersion)", "@dispersion_energy_au Ha"), ("SCF converged", "@scf_converged"),
                ("Cell A", "@cell_a_angs Angs"), ("Cell Vol", "@cell_vol_angs3 Angs^3"),
                ("MAX Step", "@max_step_au Bohr"), ("Pressure", "@pressure_bar bar")]
    hover = bmd.HoverTool(tooltips=tooltips)
    TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

    natoms = out_dict['natoms']
    values = [x / natoms * ha2u[units] for x in out_dict['step_info']['energy_au']]
    values = [x - min(values) for x in values]

    data = bmd.ColumnDataSource(data=dict(
        index=range(len(values)),
        step=out_dict['step_info']['step'],
        energy=values,
        dispersion_energy_au=out_dict['step_info']['dispersion_energy_au'],
        scf_converged=out_dict['step_info']['scf_converged'],
        cell_a_angs=out_dict['step_info']['cell_a_angs'],
        cell_vol_angs3=out_dict['step_info']['cell_vol_angs3'],
        max_step_au=out_dict['step_info']['max_step_au'],
        pressure_bar=out_dict['step_info']['pressure_bar'],
    ))

    p = figure(tools=TOOLS, title='Energy profile of the DFT minimization', height=350, width=550)

    p.xgrid.grid_line_color = None
    p.xaxis.axis_label = 'Steps'
    p.yaxis.axis_label = 'Energy ({}/atom)'.format(units)

    # Colored background
    colors = ['red', 'orange', 'green', 'yellow', 'cyan', 'pink', 'palegreen']
    start = 0
    for i, steps in enumerate(out_dict['stage_info']['nsteps']):
        end = start + steps
        p.add_layout(bmd.BoxAnnotation(left=start, right=end, fill_alpha=0.2, fill_color=colors[i]))
        start = end

    # Trace line and markers
    p.line('index', 'energy', source=data, line_color='blue')
    p.circle('index', 'energy', source=data, line_color='blue', size=3)

    return p
