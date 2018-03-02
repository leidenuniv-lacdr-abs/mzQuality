import os
import subprocess
import pandas as pd
import numpy as np

# collection of features
class Qccalc:

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

    # perform blank effect calculations
    def blank_effect(self):

        mea = self.get_mea()
        measurements = mea.get_measurements()

        blank_effect = {}
        blank_effect['compound'] = []
        blank_effect['batch'] = []
        blank_effect['be'] = []

        # Do batch specific calculations
        for batch in mea.get_batches():

            batch_index = measurements[measurements['batch'] == batch]

            # unique batch samples
            unique_batch_samples = batch_index['sample'].unique()
            unique_batch_samples.sort()

            # blank effect calculations
            for compound in mea.get_compounds():
                # get all data for this compound
                compound_index = batch_index[batch_index['compound'] == compound]
                # get compound sample
                compound_samples_index = compound_index[compound_index['type'] == 'sample']
                # get compound blank
                compound_blanks_index = compound_index[compound_index['type'] == 'blank']
                # calculate blank effect
                be_compound = (100 * (compound_blanks_index['area'].mean() / compound_samples_index['area'].mean()))

                # add the columns to the final data frame
                blank_effect['compound'].append(compound)
                blank_effect['batch'].append(batch)
                blank_effect['be'].append(be_compound)

        return pd.DataFrame(blank_effect)

    def qc_correction(self):

        mea = self.get_mea()
        measurements = mea.get_measurements()
        measurements = measurements.copy()

        # check if there are any QC samples to use
        if len(measurements[measurements['type'] == 'qc']) <= 0:
            return pd.DataFrame()  # return an empty dataframe

        # compound calculations
        for compound in measurements['compound'].unique():

            compound_index = (measurements['compound'] == compound)
            compound_qc_index = (measurements['compound'] == compound) & (measurements['type'] == 'qc') & (measurements['ratio'] > 0)

            # inter batch qc ratio median
            compound_qc_ratio_median = measurements[compound_qc_index]['ratio'].median()

            # first do intra batch qc corrections
            for batch in measurements['batch'].unique():

                compound_batch_index = (measurements['batch'] == batch) & (measurements['compound'] == compound)
                compound_qc_batch_index = (measurements['batch'] == batch) & (measurements['compound'] == compound) & (measurements['type'] == 'qc')

                # use median to level/scale ratio
                med_ratio = measurements[compound_qc_batch_index]['ratio'].median()
                qc_correct_factor = compound_qc_ratio_median / med_ratio

                # add column inter_median_qc_corrected with median corrected ratios
                measurements.ix[compound_batch_index, 'inter_median_qc_corrected'] = measurements['ratio'] * qc_correct_factor

        mea.set_measurements(measurements)

        return measurements

    def rsdqc(self):

        rsdqc = {}
        rsdqc['compound'] = []
        rsdqc['batch'] = []
        rsdqc['rsdqc_nc'] = []
        rsdqc['rsdqc_is_corrected'] = []
        rsdqc['rsdqc_inter_median_qc_corrected'] = []

        mea = self.get_mea()
        measurements = mea.get_measurements()

        # check if there are any QC samples to use
        if len(measurements[measurements['type'] == 'qc']) <= 0:
            return pd.DataFrame()  # return an empty dataframe

        for compound in mea.get_compounds():
            for batch in mea.get_batches():
                compound_batch_qc = measurements[
                    (measurements['batch'] == batch) &
                    (measurements['type'] == 'qc') &
                    (measurements['compound'] == compound)
                ]

                if len(compound_batch_qc) >= 1:
                    rsdqc_nc = 100 * (compound_batch_qc['area'].std() / compound_batch_qc['area'].mean())
                    rsdqc_is_corrected = 100 * (compound_batch_qc['ratio'].std() / compound_batch_qc['ratio'].mean())
                    rsdqc_inter_median_qc_corrected = 100 * (compound_batch_qc['inter_median_qc_corrected'].std() / compound_batch_qc['inter_median_qc_corrected'].mean())

                    rsdqc['compound'].append(compound)
                    rsdqc['batch'].append(batch)
                    rsdqc['rsdqc_nc'].append(rsdqc_nc)
                    rsdqc['rsdqc_is_corrected'].append(round(rsdqc_is_corrected, 2))
                    rsdqc['rsdqc_inter_median_qc_corrected'].append(round(rsdqc_inter_median_qc_corrected, 2))

        return pd.DataFrame(rsdqc)

    def rt_shifts(self):

        rt_shifts = {}
        rt_shifts['compound'] = []
        rt_shifts['batch'] = []
        rt_shifts['sample'] = []
        rt_shifts['rt_mean'] = []
        rt_shifts['rt_stdev'] = []
        rt_shifts['rt_shift'] = []

        mea = self.get_mea()
        measurements = mea.get_measurements()

        for compound in mea.get_compounds():
            for batch in mea.get_batches():
                compound_batch = measurements[
                    (measurements['batch'] == batch) &
                    (measurements['compound'] == compound)
                ]

                if len(compound_batch) >= 1:
                    rt_mean = np.mean(compound_batch['rt'])
                    rt_stdev = np.std(compound_batch['rt'])

                    for idx, c in compound_batch.iterrows():
                        rt_shifts['compound'].append(compound)
                        rt_shifts['batch'].append(batch)
                        rt_shifts['sample'].append(c['sample'])
                        rt_shifts['rt_mean'].append(rt_mean)
                        rt_shifts['rt_stdev'].append(rt_stdev)
                        rt_shifts['rt_shift'].append(c['rt'] - rt_mean)

        return pd.DataFrame(rt_shifts)