from jsmol_bokeh_extension import JSMol
import bokeh.models as bmd


def structure_jsmol(cif_node):

    script_source = bmd.ColumnDataSource()
    cif_str = cif_node.get_content()

    info = dict(
        height="100%",
        width="100%",
        use="HTML5",
        serverURL="https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
        j2sPath="https://chemapps.stolaf.edu/jmol/jsmol/j2s",
        #serverURL="https://www.materialscloud.org/discover/scripts/external/jsmol/php/jsmol.php",
        #j2sPath="https://www.materialscloud.org/discover/scripts/external/jsmol/j2s",
        #serverURL="details/static/jsmol/php/jsmol.php",
        #j2sPath="details/static/jsmol/j2s",
        script="""
set antialiasDisplay ON;
load data "cifstring"

{}

end "cifstring"
""".format(cif_str))

    applet = JSMol(
        width=600,
        height=600,
        script_source=script_source,
        info=info,
        #js_url="details/static/jsmol/JSmol.min.js",
    )

    return applet
