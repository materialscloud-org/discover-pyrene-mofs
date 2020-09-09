from bokeh.io import curdoc
from pipeline_config import applications, quantities, EXPLORE_URL
import panel as pn

AIIDA_LOGO_PATH = "details/static/aiida-128.png"


def get_mat_id():
    """Get the material ID from URL parameter 'mat_id', or return one for testing."""
    try:
        name = curdoc().session_context.request.arguments.get('mat_id')[0]
        if isinstance(name, bytes):
            mat_id = name.decode()
    except (TypeError, KeyError, AttributeError):
        mat_id = 'BOLZIN'

    return mat_id


def get_details_title(mat_node):
    """Get title for the Detail page."""
    title = "# Detail section for {} ({} {}) v{}".format(mat_node.extras['name_conventional'],
                                                         mat_node.extras['class_material'].upper(), mat_node.label,
                                                         mat_node.extras['workflow_version'])
    return title


def get_geom_table(zeopp):
    """Make a table of geometric properties, given the Zeopp output.

    Note: for volumetric properties I use gravimetric/Dens because in some workflow version zeopp was not parsing them.
    """
    # Usefull: ⁻¹²³⁴⁵⁶⁷⁸⁹⁰Å

    decimals = 2

    md_str = """
    ||||  
    |---|---|---|
    | Density                        | {} g/cm³ |            |
    | Access. Surface Area           | {} m²/g  | {} m²/cm³  |
    | Non-Access. Surface Area       | {} m²/g  | {} m²/cm³  |
    | Access. Geom. Pore Volume      | {} cm³/g | {} cm³/cm³ |
    | Access. Occup. Pore Volume     | {} cm³/g | {} cm³/cm³ |
    | Non-Access. Occup. Pore Volume | {} cm³/g | {} cm³/cm³ |
    | Largest Free Sphere            | {} Å     |            |
    | Largest Included Sphere        | {} Å     |            |

    """.format(
        round(zeopp["Density"], decimals),
        round(zeopp["ASA_m^2/g"], decimals),
        round(zeopp["ASA_m^2/g"] / zeopp["Density"], decimals),
        round(zeopp["NASA_m^2/g"], decimals),
        round(zeopp["NASA_m^2/g"] / zeopp["Density"], decimals),
        round(zeopp["AV_cm^3/g"], decimals),  # Remember: NAV geometric is meaningless!
        round(zeopp["AV_cm^3/g"] / zeopp["Density"], decimals),
        round(zeopp["POAV_cm^3/g"], decimals),
        round(zeopp["POAV_cm^3/g"] / zeopp["Density"], decimals),
        round(zeopp["PONAV_cm^3/g"], decimals),
        round(zeopp["PONAV_cm^3/g"] / zeopp["Density"], decimals),
        round(zeopp["Largest_free_sphere"], decimals),
        round(zeopp["Largest_included_sphere"], decimals),
    )
    return md_str


def get_appl_table(mat_nodes_dict):
    """Return table of application performance data
    
    :param dict mat_nodes_dict:  dictionary of all relevant nodes for the material
    """
    html_str = """ """
    missing_values = False
    for appl_key, appl_dict in applications.items():
        html_str += """<h3>{}</h3>""".format(appl_key)
        for propr in ["x", "y"]:
            q_dict = quantities[appl_dict[propr]]['dict']
            q_key = quantities[appl_dict[propr]]['key']
            q_unit = quantities[appl_dict[propr]]['unit']

            try:
                q_val = mat_nodes_dict[q_dict][q_key]
                #quick fix to show all values nicely enough
                if abs(float(q_val)) > 0.01:
                    q_val = round(q_val, 3)
                elif abs(float(q_val)) > 0.001:
                    q_val = round(q_val, 4)
            except:  #pylint: disable=bare-except # noqa: E722
                q_val = "***"
                missing_values = True
            html_str += "&nbsp;&nbsp;&nbsp; {} ({}): {}".format(appl_dict[propr], q_unit, q_val)

            # If the node exists (even for nonporous mat/appl) get the aiida-link
            try:
                q_uuid = mat_nodes_dict[q_dict].uuid
                html_str += get_provenance_link(q_uuid)
            except:
                pass

            html_str += "<br>"
    if missing_values:
        html_str += "<br><i>*** this property was not computed yet, incurred in some problem," +\
                    "or can not be computed for a nonpermeable system"
    return (html_str)


def get_provenance_url(uuid):
    """Return URL to EXPLORE section for given uuid."""
    return '{explore_url}/details/{uuid}'.format(explore_url=EXPLORE_URL, uuid=uuid)


def get_provenance_link(uuid, label=None):
    """Return pn.HTML representation of provenance link."""

    if label is None:
        label = "Browse provenance\n" + uuid

    html_str = "<a href='{link}' target='_blank'><img src='{logo_url}' title='{label}' class='provenance-logo'></a>"\
         .format(link=get_provenance_url(uuid), label=label, logo_url=AIIDA_LOGO_PATH)

    # return pn.pane.HTML(html_str, align='center')
    return html_str


def get_title(text, uuid=None):
    """Return pn.Row representation of title.

    Includes provenance link, if uuid is specified.
    """
    if uuid is not None:
        text += get_provenance_link(uuid)
    title = pn.Row(pn.pane.HTML('<h2>{}</h2>'.format(text)), align='start')

    return title
