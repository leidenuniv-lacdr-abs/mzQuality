import os
import time
import datetime
import pandas as pd
import numpy as np

# collection of features
class Mea:

    def __init__(self, mea_file=''):

        # init
        self.measurements = None
        self.mea_file = None

        # read in settings when provided
        if mea_file != '':
            self.set_mea_file(mea_file)
            self.read_mea_file(mea_file=self.get_mea_file())

    # set measurements file
    def set_mea_file(self, mea_file=''):
        self.mea_file = mea_file

    # get measurements file
    def get_mea_file(self):
        return self.mea_file

    # read in measurements file
    def read_mea_file(self, mea_file):

        try:

            # read raw file
            self.measurements = pd.read_csv(mea_file, sep="\t")

            # correct some fields
            self.measurements['compound'] = self.measurements['compound'].apply(lambda name: self.fix_compound_name(name))

            # add timestamp from datatime
            try:
                self.measurements['timestamp'] = self.measurements['datetime'].apply(
                    lambda x: time.mktime(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timetuple()))
            except:
                pass

            try:
                self.measurements['timestamp'] = self.measurements['datetime'].apply(
                    lambda x: time.mktime(datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S:%f").timetuple()))
            except:
                pass

            # add ratio to Pandas DataFrame
            self.measurements['ratio'] = self.measurements['area'] / self.measurements['area_is']

            # sort by batch and injection order
            self.measurements.sort_values(
                ['batch', 'order'], ascending=[True, True], inplace=True
            )

            self.measurements.reset_index()
            self.measurements['position'] = self.measurements.index + 1

        except FileExistsError:
            print("File does not exist!")

    # get measurements as Pandas DataFrame
    def get_measurements(self, drop_na=True):

        if drop_na:
            return self.measurements[np.isfinite(self.measurements['area'])]
        else:
            return self.measurements

    # set measurements as Pandas DataFrame
    def set_measurements(self, measurements):
        self.measurements = measurements

    # get measurements of samples measured in replicate
    def get_replicate_measurements(self, drop_na=True):

        measurements = self.get_measurements(drop_na=drop_na)
        replicate_samples = measurements[measurements['replicate'].isin(['', '-', '_', 'a']) == False]['sample'].unique()

        return measurements[measurements['sample'].isin(replicate_samples) == True]

    # get the unique types of all measurements
    def get_types(self):

        measurements = self.get_measurements()
        types = measurements['type'].unique()
        types.sort()

        # return sorted list of unique types in measurments
        return types

    # get the unique batch id's of all measurements
    def get_batches(self):

        measurements = self.get_measurements()
        batches = measurements['batch'].unique()
        batches.sort()

        # return sorted batch id's
        return batches

    # get the unique compounds of all measurements
    def get_compounds(self):

        measurements = self.get_measurements()
        compounds = measurements['compound'].unique()
        compounds.sort()

        # return sorted compounds
        return compounds

    # get the unique internal standards of all measurements
    def get_internal_standards(self):

        measurements = self.get_measurements()
        internal_standards = measurements['compound_is'].unique()
        internal_standards.sort()

        # return sorted compounds
        return internal_standards

    # get the unique samples of all measurements
    def get_samples(self, batch=False):

        if batch != False:
            measurements = self.get_batch_data(batch=batch)
        else:
            measurements = self.get_measurements()

        return measurements['sample'].unique()

    # get the data of a batch
    def get_batch_data(self, batch, drop_na=True):

        measurements = self.get_measurements(drop_na=drop_na)

        return measurements[measurements['batch'] == batch]

    # get the compound data
    def get_compound_data(self, compound, batch=False, drop_na=True):

        if batch:
            measurements = self.get_batch_data(batch=batch, drop_na=drop_na)
        else:
            measurements = self.get_measurements(drop_na=drop_na)

        return measurements[measurements['compound'] == compound]

    # get the internal standard data
    def get_internal_standard_data(self, internal_standard, batch=False, drop_na=True):

        if batch:
            measurements = self.get_batch_data(batch=batch, drop_na=drop_na)
        else:
            measurements = self.get_measurements(drop_na=drop_na)

        internal_standard_data = measurements[measurements['compound_is'] == internal_standard]

        return internal_standard_data.groupby('aliquot').first().reset_index()

    # provide data matrix with samples vs features
    def as_table(self, column='area', location='', include_is=False):

        # init
        sample_feature_lists = {}
        sample_feature_lists['sample'] = []
        sample_feature_lists['batch'] = []

        # prepare header
        cols = []
        cols.append('sample')
        cols.append('batch')

        # add compound names to header
        for compound in self.get_compounds():
            cols.append(compound)

            if include_is:
                cols.append(compound + '_IS')

            sample_feature_lists[compound] = []

            if include_is:
                sample_feature_lists[compound + '_IS'] = []

        measurements = self.get_measurements()

        for batch in self.get_batches():
            for sample in self.get_samples(batch=batch):  # get batch specific samples

                sample_feature_lists['sample'].append(sample)
                sample_feature_lists['batch'].append(batch)

                for compound in self.get_compounds():

                    batch_sample_compound = measurements[
                        (measurements['batch'] == batch) &
                        (measurements['sample'] == sample) &
                        (measurements['compound'] == compound)
                    ]

                    # some compounds may not be in all batches, add 0 there
                    try:
                        value = batch_sample_compound.iloc[0][column]
                    except:
                        value = 0.0

                    if include_is:
                        try:
                            value_is = batch_sample_compound.iloc[0]['area_is']
                        except:
                            value_is = 0.0

                    # include the value
                    sample_feature_lists[compound].append(float(value))

                    if include_is:
                        sample_feature_lists[compound + '_IS'].append(float(value_is))

        data_matrix = pd.DataFrame(sample_feature_lists)
        data_matrix = data_matrix[cols]  # put sample and batch in first 2 columns

        if not location:
            return data_matrix
        else:
            data_matrix.to_csv(location, sep="\t", index=False, encoding='utf-8')

        return True

    # *************************************
    # HELPER FUNCTIONS
    # *************************************

    # correct compound names in measurements
    def fix_compound_name(self, name):

        changelist = {' ': '_', '*': '_star', '%': '_pct', '&': '_and', ',': '_'}
        changelist = str.maketrans(changelist)
        name = str(name).translate(changelist)
        return name
