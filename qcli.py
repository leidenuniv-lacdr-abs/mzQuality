#! /usr/bin/env python3

""" QC CLI interface """
import os
import sys
import fire
import json
import time
import datetime
from subprocess import run, Popen, PIPE
from src.lib.mea import Mea
from src.lib.qccalc import Qccalc
from src.lib.qcplot import Qcplot

class Qcli(object):
    """ CLI to the mzQuality

        mzQuality is a Tool for quality monitoring and reporting of mass spectrometry measurements.

        Supported methods are:

        - measurement summary
        - blank_effect
        - rt_shifts
        - qc_correction
        - rsdqc
        - plot compound information
        - export results as samples vs. compounds
    """

    def summary(self, mea_file):
        """ Report a summary of the measurements ... """

        try:
            # load measurements file
            mea = Mea(mea_file)

            # build summary dict
            summary = {
                'batches': mea.get_batches().tolist(),
                'samples': mea.get_samples().tolist(),
                'compounds': mea.get_compounds().tolist()
            }
        except:
            summary = {}

        # return a json encoded dict
        return json.JSONEncoder().encode(summary)

    def blank_effect(self, mea_file, blank_effect_file):
        """ Calculate the blank effect of ... """

        # load measurements file
        mea = Mea(mea_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate blank effect
        blank_effect = qccalc.blank_effect()

        # save results to file
        blank_effect.to_csv(blank_effect_file, sep="\t", index=False, encoding='utf-8')

    def rt_shifts(self, mea_file, rt_shifts_file):
        """ Calculate the RT shifts of each compound per batch ... """

        # load measurements file
        mea = Mea(mea_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate qc rsd's
        rt_shifts = qccalc.rt_shifts()

        # save results to file
        rt_shifts.to_csv(rt_shifts_file, sep="\t", index=False, encoding='utf-8')

    def qc_correction(self, mea_file, qc_corrected_file):
        """ Calculate the QC corrected data ... """

        # load measurements file
        mea = Mea(mea_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate qc corrected data
        qc_corrected = qccalc.qc_correction()

        # save results to file
        qc_corrected.to_csv(qc_corrected_file, sep="\t", index=False, encoding='utf-8')

    def qc_rsd(self, qc_corrected_file, qc_rsd_file, by_batch=False):
        """ Calculate the QC RSD's ... """

        # load measurements file
        mea = Mea(qc_corrected_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate qc rsd's
        rsdqc = qccalc.rsdqc(by_batch=by_batch)

        # save results to file
        rsdqc.to_csv(qc_rsd_file, sep="\t", index=False, encoding='utf-8')

    def rep_rsd(self, qc_corrected_file, rep_rsd_file, by_batch=False):
        """ Calculate the Replicate RSD's ... """

        # load measurements file
        mea = Mea(qc_corrected_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate qc rsd's
        rsdqc = qccalc.rsdrep(by_batch=by_batch)

        # save results to file
        rsdqc.to_csv(rep_rsd_file, sep="\t", index=False, encoding='utf-8')

    def plot_compound(self, qc_corrected_file, compound, plot_location):
        """ plot an individual compound """

        # load measurements file
        mea = Mea(qc_corrected_file)

        # init plot class
        qcplot = Qcplot(mea=mea)

        # plot the compound
        qcplot.plot_compound_qc_data(compound=compound, location=plot_location)

    def export_measurements(self, file, column, export_location, include_is=False):
        """ exports data as samples vs compounds"""

        # load measurements file
        mea = Mea(file)

        # store as table
        mea.as_table(column=column, location=export_location, include_is=include_is)

    def test_cli(self):
        """ Test all methods of the API with one command"""

        # input vars
        command_prefix = 'python qcli.py'
        mea_file = './data/combined.tsv'
        blank_effect_file = './data/blank_effect.tsv'
        rt_shifts_file = './data/rt_shifts.tsv'
        qc_corrected_file = './data/qc_corrected.tsv'
        qc_rsd_file = './data/rsdqc.tsv'
        batch_qc_rsd_file = './data/batch_rsdqc.tsv'
        rep_rsd_file = './data/rsdrep.tsv'
        batch_rep_rsd_file = './data/batch_rsdrep.tsv'
        plot_location = './data/plots/'

        export_area_file = mea_file
        export_area_column = 'area'
        export_area_location = './data/area.tsv'
        export_area_is = True

        export_ratio_file = mea_file
        export_ratio_column = 'ratio'
        export_ratio_location = './data/ratio.tsv'
        export_ratio_is = False

        export_qc_inter_file = qc_corrected_file
        export_qc_inter_column = 'inter_median_qc_corrected'
        export_qc_inter_location = './data/qc_inter.tsv'
        export_qc_inter_is = False

        try:

            # result summary
            print("Test results ({}):".format(
                datetime.datetime.fromtimestamp(
                    time.time()).strftime('%Y-%m-%d %H:%M:%S')))

            # summary
            summary_proc = Popen("{} summary --mea-file={}".format(command_prefix, mea_file), stdout=PIPE, shell=True)
            out, err = summary_proc.communicate(timeout=15)
            summary = json.loads(out.decode('utf8'))
            batches = summary['batches']
            samples = summary['samples']
            compounds = summary['compounds']

            print("Found {} batches, {} samples, and {} compounds.".format(
                len(batches), len(samples), len(compounds)))

            # blank effect
            run("{} blank-effect --mea-file={} --blank-effect-file={}".format(
                command_prefix,
                mea_file, blank_effect_file
            ), shell=True, check=True)
            print(" - blank effect passed...")

            # rt shifts
            run("{} rt-shifts --mea-file={} --rt-shifts-file={}".format(
                command_prefix,
                mea_file, rt_shifts_file
            ), shell=True, check=True)
            print(" - rt-shifts passed...")

            # qc correction
            run("{} qc-correction --mea-file={} --qc-corrected-file={}".format(
                command_prefix,
                mea_file, qc_corrected_file
            ), shell=True, check=True)
            print(" - qc-correction passed...")

            # qc rsd
            run("{} qc-rsd --qc-corrected-file={} --qc-rsd-file={}".format(
                command_prefix,
                qc_corrected_file, qc_rsd_file
            ), shell=True, check=True)
            print(" - qc-rsd passed...")

            run("{} qc-rsd --qc-corrected-file={} --qc-rsd-file={} --by-batch={}".format(
                command_prefix,
                qc_corrected_file, batch_qc_rsd_file, True
            ), shell=True, check=True)
            print(" - qc-rsd by batch passed...")

            # rep rsd
            run("{} rep-rsd --qc-corrected-file={} --rep-rsd-file={}".format(
                command_prefix,
                qc_corrected_file, rep_rsd_file
            ), shell=True, check=True)
            print(" - rep-rsd passed...")

            run("{} rep-rsd --qc-corrected-file={} --rep-rsd-file={} --by-batch={}".format(
                command_prefix,
                qc_corrected_file, batch_rep_rsd_file, True
            ), shell=True, check=True)
            print(" - rep-rsd by batch passed...")

            # export_measurements (area)
            run("{} export_measurements --file={} --column={} --export_location={} --include_is={}".format(
                command_prefix,
                export_area_file, export_area_column, export_area_location, export_area_is
            ), shell=True, check=True)
            print(" - export area's passed...")

            # export_measurements (ratio)
            run("{} export_measurements --file={} --column={} --export_location={} --include_is={}".format(
                command_prefix,
                export_ratio_file, export_ratio_column, export_ratio_location, export_ratio_is
            ), shell=True, check=True)
            print(" - export ratio's passed...")

            # export_measurements (qc_corrected)
            run("{} export_measurements --file={} --column={} --export_location={} --include_is={}".format(
                command_prefix,
                export_qc_inter_file, export_qc_inter_column, export_qc_inter_location, export_qc_inter_is
            ), shell=True, check=True)
            print(" - export qc_inter passed...")

            # plot (a limited number of) compounds
            print(" + plot compounds:")
            for compound in compounds:
                run("{} plot_compound --qc-corrected-file={} --compound={} --plot-location={}".format(
                    command_prefix,
                    qc_corrected_file, compound, plot_location
                ), shell=True, check=True)
                print("  - plot compound {} passed...".format(compound))

        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

if __name__ == '__main__':
    fire.Fire(Qcli)