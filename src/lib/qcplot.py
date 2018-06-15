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
        colormap[0] = ['#4CBB3E','#49B842','#46B546','#44B24B','#41AF4F','#3EAC54','#3CA958','#39A65D','#37A361','#34A066','#319D6A','#2F9A6E','#2C9773','#299477','#27917C','#248F80','#228C85','#1F8989','#1C868E','#1A8392','#178096','#147D9B','#127A9F','#0F77A4','#0D74A8','#0A71AD','#076EB1','#056BB6','#0268BA','#0066BF']
        colormap[1] = ['#4CBB3E','#49B842','#46B546','#44B24B','#41AF4F','#3EAC54','#3CA958','#39A65D','#37A361','#34A066','#319D6A','#2F9A6E','#2C9773','#299477','#27917C','#248F80','#228C85','#1F8989','#1C868E','#1A8392','#178096','#147D9B','#127A9F','#0F77A4','#0D74A8','#0A71AD','#076EB1','#056BB6','#0268BA','#0066BF']
        colormap[2] = ['#4CBB3E','#49B842','#46B546','#44B24B','#41AF4F','#3EAC54','#3CA958','#39A65D','#37A361','#34A066','#319D6A','#2F9A6E','#2C9773','#299477','#27917C','#248F80','#228C85','#1F8989','#1C868E','#1A8392','#178096','#147D9B','#127A9F','#0F77A4','#0D74A8','#0A71AD','#076EB1','#056BB6','#0268BA','#0066BF']

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
        fig = tools.make_subplots(rows=4, cols=1,
                                  vertical_spacing=0.1,
                                  print_grid=True,
                                  shared_xaxes=True,
                                  shared_yaxes=False,
                                  subplot_titles=(
                                      'Area',
                                      'Internal Standard corrected (ratio)',
                                      'QC corrected',
                                      'Retention time'
                                  )
        )

        fig['layout'].update(margin=dict(
                                r=100,
                                t=100,
                                b=300,
                                l=100),
                                paper_bgcolor='#e4e4e4',
                                plot_bgcolor='#ffffff',
                                autosize=True,
                                title="mzQuality results {}".format(compound))

        # start with adding the median area in all batches
        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=np.zeros(len(meas['aliquot'])),
            mode='markers',
            showlegend=False,
            marker=dict(
                size=1,
                color='rgba(255, 255, 255, 0.0)',
            )
        ), row, 1)

        colormap = self.get_colormap(level=0)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                    x=batch_sample_mea['aliquot'],
                    y=batch_sample_mea['area'],
                    mode='markers',
                    marker=dict(size=8, color=colormap[batch-1]),
                    name="batch {}".format(batch)
            ), row, 1)

        fig.append_trace(go.Scatter(
                x=sample_measurements['aliquot'],
                y=sample_measurements['area_is'],
                mode='markers',
                marker=dict(size=8, color='#000'),
                visible='legendonly',
            name="internal standard"
        ), row, 1)

        fig.append_trace(go.Scatter(
                x=cal_measurements['aliquot'],
                y=cal_measurements['area'],
                mode='markers',
                name="cals",
                visible='legendonly',
                marker=dict(
                    color='rgba(0, 0, 0, .5)',
                )
        ), row, 1)

        fig.append_trace(go.Scatter(
                x=blank_measurements['aliquot'],
                y=blank_measurements['area'],
                mode='markers',
                name="blanks",
                visible='legendonly',
                marker=dict(
                    color='rgba(255, 255, 0, 1.0)',
                )
        ), row, 1)

        fig.append_trace(go.Scatter(
            x=qc_measurements['aliquot'],
            y=qc_measurements['area'],
            mode='markers',
            name="qc",
            visible='legendonly',
            marker=dict(
                color='rgba(0, 182, 193, .9)'
            )), row, 1)

        row += 1
        colormap = self.get_colormap(level=1)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                x=batch_sample_mea['aliquot'],
                y=batch_sample_mea['ratio'],
                mode='markers',
                marker=dict(size=8, color=colormap[batch-1]),
                name="ratios batch {}".format(batch)
            ), row, 1)

        row += 1
        colormap = self.get_colormap(level=2)
        colormap = colormap[::int(len(colormap)/len(mea.get_batches())-1)]
        for batch, batch_sample_mea in sample_batch_measurements:
            fig.append_trace(go.Scatter(
                x=batch_sample_mea['aliquot'],
                y=batch_sample_mea['inter_median_qc_corrected'],
                mode='markers',
                marker=dict(size=8, color=colormap[batch-1]),
                name="QC corrected batch {}".format(batch)
            ), row, 1)

        row += 1
        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=meas['rt'],
            mode='markers',
            name="rt",
            marker=dict(
                color='rgba(0, 0, 0, 1.0)'
            )), row, 1)

        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=meas['rt_is'],
            mode='markers',
            name="rt internal standard",
            marker=dict(
                color='rgba(250, 0, 0, 1.0)'
            )), row, 1)

        vals = np.empty(len(meas['rt']))
        vals.fill(meas['rt'].median())
        fig.append_trace(go.Scatter(
            x=meas['aliquot'],
            y=vals,
            mode='lines',
            name="median rt",
            line=dict(
                color=('rgb(192, 192, 192)'),
                width=1)
        ), row, 1)

        plot(fig, filename="{}/{}.html".format(location, compound), auto_open=False, show_link=False)

        return True