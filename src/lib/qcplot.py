import os
from bokeh.plotting import *
from bokeh.models import ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file
from bokeh.models import CustomJS
from bokeh.models import HoverTool

# collection of features
class Qcplot:

    def __init__(self, mea=''):

        # init
        self.mea = None

        # read in settings when provided
        if mea != '':
            self.set_mea(mea)

    # set mea
    def set_mea(self, mea=''):
        self.mea = mea

    # get mea
    def get_mea(self):
        return self.mea

    def plot_compound_qc_data(self, compound=False, location=''):

        # load data
        mea = self.get_mea()
        meas = mea.get_compound_data(compound=compound)

        # prepare location
        try:
            os.mkdir(location)
        except:
            pass

        # init re-usable variables
        p_width = 1600
        p_height = 500

        visible_tools = 'hover,pan,wheel_zoom,box_zoom,reset,crosshair,save'

        axis_label = "injection order"
        axis_line_width = 2
        major_label_text_color = "black"
        major_label_orientation = "horizontal"
        dot_size = 12

        color_map = {
            1: 'green',
            2: 'orange',
            3: 'blue',
            4: 'yellow',
            5: 'brown',
            6: 'pink',
            7: 'green',
            8: 'orange',
            9: 'blue',
            10: 'yellow',
            11: 'brown',
            12: 'pink',
            13: 'green',
            14: 'orange',
            15: 'blue',
            16: 'yellow',
            17: 'brown',
            18: 'pink',
            19: 'green',
            20: 'orange',
            21: 'blue',
            22: 'yellow',
            23: 'brown',
            24: 'pink'
        }

        color_map_types = {
            'qc': 'red',
            'cal': 'cyan',
            'blank': 'grey',
            'sample': 'green',
        }

        # prepare some data
        html_location = "{}/{}_plot.html".format(location, compound)

        # remove old html
        if os.path.exists(html_location):
            os.remove(html_location)

        # set html location
        output_file(html_location)

        # start first figure, plot the area data
        fig_area = figure(
            plot_width=p_width,
            plot_height=p_height,
            tools=visible_tools,
            title=compound
        )

        fig_area.min_border_top = 120

        for batch in mea.get_batches():

            # filter batch sample data
            batch_data = meas[(meas['batch'] == batch) & (meas['type'] == 'sample')]

            # add areas to figure
            fig_name = "fig_area_batch_{}".format(batch)
            fig_area.circle(
                source=ColumnDataSource(
                    data=batch_data
                ),
                x='position',
                y='area',
                name=fig_name,
                legend="batch {}".format(batch),
                color=color_map[batch],
                size=dot_size
            )

            # add the tooltips
            h = HoverTool(names=[fig_name])
            h.tooltips = [(c, '@' + c) for c in batch_data.columns]
            h.tooltips.append(('index', '$index'))
            fig_area.add_tools(h)

        # add qc to figure
        fig_name = "fig_area_is"
        fig_area.circle(
            source=ColumnDataSource(
                data=meas
            ),
            x='position',
            y='area_is',
            name=fig_name,
            legend="Internal Standard",
            color="black",
            size=dot_size
        )

        # add the tooltips
        h = HoverTool(names=[fig_name])
        h.tooltips = [(c, '@' + c) for c in meas.columns]
        h.tooltips.append(('index', '$index'))
        fig_area.add_tools(h)

        for t in mea.get_types():
            if t != 'sample':

                # get data for this type
                type_data = meas[meas['type'] == t]

                # add this data type to the figure
                fig_name = "fig_area_types_{}".format(t)
                fig_area.circle(
                    source=ColumnDataSource(
                        data=type_data
                    ),
                    x='position',
                    y='area',
                    name=fig_name,
                    legend=t,
                    size=dot_size,
                    color=color_map_types[t]
                )

                # add the tooltips
                h = HoverTool(names=[fig_name])
                h.tooltips = [(c, '@' + c) for c in type_data.columns]
                h.tooltips.append(('index', '$index'))
                fig_area.add_tools(h)

        fig_area.xaxis.axis_label = axis_label
        fig_area.xaxis.axis_line_width = axis_line_width
        fig_area.yaxis.axis_label = "Area"
        fig_area.yaxis.major_label_text_color = major_label_text_color
        fig_area.yaxis.major_label_orientation = major_label_orientation


        # start second figure, plot the ratio data
        fig_ratio = figure(
            plot_width=p_width,
            plot_height=p_height,
            tools=visible_tools,
            title=compound
        )

        for batch in mea.get_batches():

            # filter batch data
            batch_data = meas[(meas['batch'] == batch) & (meas['type'] == 'sample')]

            # add ratios to figure
            fig_name = "fig_ratio_batch_{}".format(batch)
            fig_ratio.circle(
                source=ColumnDataSource(
                    data=batch_data
                ),
                x='position',
                y='ratio',
                name=fig_name,
                legend="batch {}".format(batch),
                size=dot_size,
                color=color_map[batch]
            )

            # add the tooltips
            h = HoverTool(names=[fig_name])
            h.tooltips = [(c, '@' + c) for c in batch_data.columns]
            h.tooltips.append(('index', '$index'))
            fig_ratio.add_tools(h)

        for t in mea.get_types():
            if t != 'sample':

                # get data for this type
                type_data = meas[meas['type'] == t]

                # add this data type to the figure
                fig_name = "fig_ratio_types_{}".format(t)
                fig_ratio.circle(
                    source=ColumnDataSource(
                        data=type_data
                    ),
                    x='position',
                    y='ratio',
                    name=fig_name,
                    legend=t,
                    size=dot_size,
                    color=color_map_types[t]
                )

                # add the tooltips
                h = HoverTool(names=[fig_name])
                h.tooltips = [(c, '@' + c) for c in type_data.columns]
                h.tooltips.append(('index', '$index'))
                fig_ratio.add_tools(h)

        fig_ratio.xaxis.axis_label = axis_label
        fig_ratio.xaxis.axis_line_width = axis_line_width
        fig_ratio.yaxis.axis_label = "Ratio"
        fig_ratio.yaxis.major_label_text_color = major_label_text_color
        fig_ratio.yaxis.major_label_orientation = major_label_orientation

        # start second figure, plot the ratio (qc corrected) data
        fig_ratio_qc = figure(
            plot_width=p_width,
            plot_height=p_height,
            tools=visible_tools,
            title=compound
        )

        for batch in mea.get_batches():

            # filter batch data
            batch_data = meas[(meas['batch'] == batch) & (meas['type'] == 'sample')]

            # add ratios to figure
            fig_name = "fig_ratio_qc_corrected_batch_{}".format(batch)
            fig_ratio_qc.circle(
                source=ColumnDataSource(
                    data=batch_data
                ),
                x='position',
                y='inter_median_qc_corrected',
                name=fig_name,
                legend="batch {}".format(batch),
                size=dot_size,
                color=color_map[batch]
            )

            # add the tooltips
            h = HoverTool(names=[fig_name])
            h.tooltips = [(c, '@' + c) for c in batch_data.columns]
            h.tooltips.append(('index', '$index'))
            fig_ratio_qc.add_tools(h)

        for t in mea.get_types():
            if t != 'sample':

                # get data for this type
                type_data = meas[meas['type'] == t]

                # add this data type to the figure
                fig_name = "fig_ratio_qc_corrected_types_{}".format(t)
                fig_ratio_qc.circle(
                    source=ColumnDataSource(
                        data=type_data
                    ),
                    x='position',
                    y='inter_median_qc_corrected',
                    name=fig_name,
                    legend=t,
                    size=dot_size,
                    color=color_map_types[t]
                )

                # add the tooltips
                h = HoverTool(names=[fig_name])
                h.tooltips = [(c, '@' + c) for c in type_data.columns]
                h.tooltips.append(('index', '$index'))
                fig_ratio_qc.add_tools(h)

        fig_ratio_qc.xaxis.axis_label = axis_label
        fig_ratio_qc.xaxis.axis_line_width = axis_line_width
        fig_ratio_qc.yaxis.axis_label = "Ratio (QC corrected)"
        fig_ratio_qc.yaxis.major_label_text_color = major_label_text_color
        fig_ratio_qc.yaxis.major_label_orientation = major_label_orientation

        # start third figure, plot the RT data
        fig_rt = figure(
            plot_width=p_width,
            plot_height=p_height,
            tools=visible_tools,
            title=compound)

        for batch in mea.get_batches():

            # filter batch data
            batch_data = meas[(meas['batch'] == batch) & (meas['type'] == 'sample')]

            fig_name = "fig_rt_batch_{}".format(batch)
            fig_rt.circle(
                source=ColumnDataSource(
                    data=batch_data
                ),
                name=fig_name,
                x='position',
                y='rt',
                legend="batch {}".format(batch),
                size=dot_size,
                color=color_map[batch]
            )

            # add the tooltips
            h = HoverTool(names=[fig_name])
            h.tooltips = [(c, '@' + c) for c in batch_data.columns]
            h.tooltips.append(('index', '$index'))
            fig_rt.add_tools(h)

        for t in mea.get_types():
            if t != 'sample':

                # get data for this type
                type_data = meas[meas['type'] == t]

                # add this data type to the figure
                fig_name = "fig_rt_types_{}".format(t)
                fig_rt.circle(
                    source=ColumnDataSource(
                        data=type_data
                    ),
                    x='position',
                    y='rt',
                    name=fig_name,
                    legend=t,
                    size=dot_size,
                    color=color_map_types[t]
                )


                # add the tooltips
                h = HoverTool(names=[fig_name])
                h.tooltips = [(c, '@' + c) for c in type_data.columns]
                h.tooltips.append(('index', '$index'))
                fig_rt.add_tools(h)


        fig_rt.xaxis.axis_label = axis_label
        fig_rt.xaxis.axis_line_width = axis_line_width
        fig_rt.yaxis.axis_label = "RT"
        fig_rt.yaxis.major_label_text_color = major_label_text_color
        fig_rt.yaxis.major_label_orientation = major_label_orientation


        # show the different plots
        save(gridplot([fig_area], [fig_ratio], [fig_ratio_qc], [fig_rt]))

        callback = CustomJS(code="""
            var tooltips = document.getElementsByClassName("bk-tooltip");
            for (var i = 0, len = tooltips.length; i < len; i ++) {
                tooltips[i].style.top = ""; // unset what bokeh.js sets
                tooltips[i].style.left = "";
                tooltips[i].style.bottom = "0px";
                tooltips[i].style.left = "0px";
            }
            """)