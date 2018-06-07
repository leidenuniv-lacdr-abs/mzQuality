import os
import numpy as np
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

        # plot layout
        layout = go.Layout(
            autosize=True,
            margin=dict(
                l=50,
                r=50,
                b=200,
                t=50,
                pad=10
            ),
            xaxis=dict(
                title="QCTool - {}".format(compound),
                titlefont=dict(
                    family='Arial, sans-serif',
                    size=28,
                    color='grey'
                ),
                showticklabels=True,
                autotick=True,
                tickangle=90,
                tickfont=dict(
                    family='Arial, sans-serif',
                    size=12,
                    color='black'
                )
            )
        )

        updatemenus = list([
            dict(
                active=0,
                buttons=list([
                    dict(
                        args=[{'visible': [True, True, True, True, True, True, True, False]}],
                        label='All',
                        method='update'
                    ),
                    dict(
                        args=[{'visible': [False, True, True, True, True, False, False, False]}],
                        label='Samples',
                        method='update'
                    ),
                    dict(
                        args=[{'visible': [False, False, False, False, False, False, True, False]}],
                        label='QCs',
                        method='update'
                    ),
                    dict(
                        args=[{'visible': [False, False, False, False, False, False, False, True]}],
                        label='RT',
                        method='update'
                    )
                ]),
                direction='down',
                pad={'r': 10, 't': 5},
                showactive=True,
                x=0.1,
                xanchor='left',
                y=1.1,
                yanchor='top'
            ),
        ])

        plot_data = []

        # start with adding the median area in all batches
        plot_data.append(go.Scatter(
            x=meas['position'],
            y=np.zeros(len(meas['sample'])),
            mode='markers',
            showlegend=False,
            marker=dict(
                size=1,
                color='rgba(255, 255, 255, 0.0)',
            )
        ))

        for batch, batch_sample_mea in sample_batch_measurements:
            plot_data.append(go.Scatter(
                    x=batch_sample_mea['position'],
                    y=batch_sample_mea['area'],
                    mode='markers',
                    marker=dict(size=8),
                    name="batch {}".format(batch)
            ))

        plot_data.append(go.Scatter(
                x=cal_measurements['position'],
                y=cal_measurements['area'],
                mode='markers',
                name="cals",
                marker=dict(
                    color='rgba(0, 0, 0, .5)',
                )
        ))

        plot_data.append(go.Scatter(
                x=blank_measurements['position'],
                y=blank_measurements['area'],
                mode='markers',
                name="blanks",
                marker=dict(
                    color='rgba(255, 255, 0, 1.0)',
                )
        ))

        plot_data.append(go.Scatter(
                x=qc_measurements['position'],
                y=qc_measurements['area'],
                mode='markers',
                name="qc",
                marker=dict(
                    color='rgba(0, 182, 193, .9)'
                )))

        plot_data.append(go.Scatter(
                x=meas['position'],
                y=meas['rt'],
                visible=False,
                mode='markers',
                name="rt",
                marker=dict(
                    color='rgba(0, 0, 0, 1.0)'
                )))

        layout['updatemenus'] = updatemenus

        fig = dict(data=plot_data, layout=layout)

        plot(fig,
            filename="{}/{}.html".format(location, compound),
            auto_open=False,
            show_link=False,
        )

        return True