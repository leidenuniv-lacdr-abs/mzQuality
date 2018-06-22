import os
import numpy as np
from plotly import tools
from plotly.offline import plot
import plotly.graph_objs as go

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

    # get color maps
    def get_colormap(self, level=0):

        colormap = {}
        colormap[0] = ['#4CBB3E90', '#49B84290', '#46B54690', '#44B24B90', '#41AF4F90', '#3EAC5490', '#3CA95890', '#39A65D90', '#37A36190', '#34A06690', '#319D6A90', '#2F9A6E90', '#2C977390', '#29947790', '#27917C90', '#248F8090', '#228C8590', '#1F898990', '#1C868E90', '#1A839290', '#17809690', '#147D9B90', '#127A9F90', '#0F77A490', '#0D74A890', '#0A71AD90', '#076EB190', '#056BB690', '#0268BA90', '#0066BF90']
        colormap[1] = ['#4CBB3E80', '#49B84280', '#46B54680', '#44B24B80', '#41AF4F80', '#3EAC5480', '#3CA95880', '#39A65D80', '#37A36180', '#34A06680', '#319D6A80', '#2F9A6E80', '#2C977380', '#29947780', '#27917C80', '#248F8080', '#228C8580', '#1F898980', '#1C868E80', '#1A839280', '#17809680', '#147D9B80', '#127A9F80', '#0F77A480', '#0D74A880', '#0A71AD80', '#076EB180', '#056BB680', '#0268BA80', '#0066BF80']
        colormap[2] = ['#4CBB3E', '#49B842', '#46B546', '#44B24B', '#41AF4F', '#3EAC54', '#3CA958', '#39A65D', '#37A361', '#34A066', '#319D6A', '#2F9A6E', '#2C9773', '#299477', '#27917C', '#248F80', '#228C85', '#1F8989', '#1C868E', '#1A8392', '#178096', '#147D9B', '#127A9F', '#0F77A4', '#0D74A8', '#0A71AD', '#076EB1', '#056BB6', '#0268BA', '#0066BF']

        return list(reversed(colormap[level]))


    def plot_compound_qc_data(self, compound=False, location=''):

        # load data
        mea = self.get_mea()
        meas = mea.get_compound_data(compound=compound)

        # prepare sets
        sample_measurements = meas[meas['type'] == 'sample']
        sample_batch_measurements = sample_measurements.groupby('batch')

        cal_measurements = meas[meas['type'] == 'cal']
        blank_measurements = meas[meas['type'] == 'blank']
        qc_measurements = meas[meas['type'] == 'qc']

        # prepare location
        try:
            os.mkdir(location)
        except:
            pass

        row = 1
        fig = tools.make_subplots(rows=3, cols=1,
                                  vertical_spacing=0.025,
                                  print_grid=False,
                                  shared_xaxes=True,
                                  shared_yaxes=False,
                                  subplot_titles=(
                                      'Area',
                                      'Internal STD & QC corrected (ratio)',
                                      'Retention time'
                                  )
        )

        fig['layout'].update(margin=dict(r=40, t=100, b=400, l=100),
            paper_bgcolor='#e4e4e4',
            plot_bgcolor='#ffffff',
            autosize=True,
            font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
            title="mzQuality results {}".format(compound))

        # First subplot, non-corrected data

        # force all aliquots in the x-axis
        fig.append_trace(go.Scatter(
            x=meas['aliquot'], y=np.zeros(len(meas['aliquot'])), mode='markers', showlegend=False,
            marker=dict(size=1, color='rgba(255, 255, 255, 0.0)', )
        ), row, 1)

        colormap = self.get_colormap(level=0)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                    x=batch_sample_mea['aliquot'],
                    y=batch_sample_mea['area'],
                    mode='markers',
                    marker=dict(size=8, color=colormap[batch-1]),
                    name="Batch {}".format(batch)
            ), row, 1)

        fig.append_trace(go.Scatter(
                x=sample_measurements['aliquot'],
                y=sample_measurements['area_is'],
                mode='markers',
                marker=dict(size=8, color='#000'),
                visible='legendonly',
                name="Internal STD"
        ), row, 1)

        fig.append_trace(go.Scatter(
                x=cal_measurements['aliquot'],
                y=cal_measurements['area'],
                mode='markers',
                name="Cals",
                visible='legendonly',
                marker=dict(
                    color='rgba(0, 0, 0, .5)',
                )
        ), row, 1)

        fig.append_trace(go.Scatter(
                x=blank_measurements['aliquot'],
                y=blank_measurements['area'],
                mode='markers',
                name="Blanks",
                visible='legendonly',
                marker=dict(
                    color='rgba(227, 45, 6, 1.0)',
                )
        ), row, 1)

        fig.append_trace(go.Scatter(
            x=qc_measurements['aliquot'],
            y=qc_measurements['area'],
            mode='markers',
            name="QC",
            visible='legendonly',
            marker=dict(
                color='rgba(0, 182, 193, .9)'
            )), row, 1)


        # next subplot (Internal STD & QC corrected)
        row += 1

        # force all aliquots in the x-axis
        fig.append_trace(go.Scatter(
            x=meas['aliquot'], y=np.zeros(len(meas['aliquot'])), mode='markers', showlegend=False,
            marker=dict(size=1, color='rgba(255, 255, 255, 0.0)', )
        ), row, 1)

        colormap = self.get_colormap(level=1)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                x=batch_sample_mea['aliquot'],
                y=batch_sample_mea['ratio'],
                mode='markers',
                marker=dict(size=8, color=colormap[batch-1]),
                name="Int.STD corr (batch {})".format(batch)
            ), row, 1)

        colormap = self.get_colormap(level=2)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                x=batch_sample_mea['aliquot'],
                y=batch_sample_mea['inter_median_qc_corrected'],
                mode='markers',
                marker=dict(size=8, color=colormap[batch-1]),
                name="QC corr. batch {}".format(batch)
            ), row, 1)

        # next subplot (QC corrected)
        row += 1

        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=meas['rt'],
            mode='markers',
            name="RT",
            marker=dict(
                color='rgba(0, 0, 0, 1.0)'
            )), row, 1)

        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=meas['rt_is'],
            mode='markers',
            name="RT Internal STD",
            marker=dict(
                color='rgba(250, 0, 0, .3)'
            )), row, 1)

        vals = np.empty(len(meas['rt']))
        vals.fill(meas['rt'].median())
        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=vals,
            mode='lines',
            name="RT (median)",
            line=dict(
                color=('rgb(192, 192, 192)'),
                width=1)
        ), row, 1)

        plot_location = "{}/{}.html".format(location, compound)
        plot(fig, filename=plot_location, auto_open=False, show_link=False)

        return plot_location