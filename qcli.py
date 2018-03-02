#! /usr/bin/env python3

""" QC CLI interface """
import os
import sys
import fire
import json
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
        - plot the ...
        - and ...
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

    def qc_rsd(self, qc_corrected_file, qc_rsd_file):
        """ Calculate the QC RSD's ... """

        # load measurements file
        mea = Mea(qc_corrected_file)

        # init calc class
        qccalc = Qccalc(mea=mea)

        # calculate qc rsd's
        rsdqc = qccalc.rsdqc()

        # save results to file
        rsdqc.to_csv(qc_rsd_file, sep="\t", index=False, encoding='utf-8')

    def plot_compound(self, qc_corrected_file, compound, plot_location):
        """ plot an individual compound """

        # load measurements file
        mea = Mea(qc_corrected_file)

        # init plot class
        qcplot = Qcplot(mea=mea)

        # plot the compound
        qcplot.plot_compound_qc_data(compound=compound, location=plot_location)

    def test_cli(self):
        """ Test all methods of the API with one command"""

        # input vars
        command_prefix = './qcli.py'
        mea_file = './data/combined.tsv'
        blank_effect_file = './data/blank_effect.tsv'
        rt_shifts_file = './data/rt_shifts.tsv'
        qc_corrected_file = './data/qc_corrected.tsv'
        qc_rsd_file = './data/rsdqc.tsv'
        plot_location = './data/plots/'

        try:

            # summary
            summary_proc = Popen([command_prefix, "summary", "--mea-file={}".format(mea_file)], stdout=PIPE)
            out, err = summary_proc.communicate(timeout=15)
            summary = json.loads(out.decode('utf8'))
            batches = summary['batches']
            samples = summary['samples']
            compounds = summary['compounds']

            # blank effect
            run("{} blank-effect --mea-file={} --blank-effect-file={}".format(
                command_prefix,
                mea_file,
                blank_effect_file
            ), shell=True, check=True)

            # rt shifts
            run("{} rt-shifts --mea-file={} --rt-shifts-file={}".format(
                command_prefix,
                mea_file,
                rt_shifts_file
            ), shell=True, check=True)

            # qc correction
            run("{} qc-correction --mea-file={} --qc-corrected-file={}".format(
                command_prefix,
                mea_file,
                qc_corrected_file
            ), shell=True, check=True)

            # qc rsd
            run("{} qc-rsd --qc-corrected-file={} --qc-rsd-file={}".format(
                command_prefix,
                qc_corrected_file,
                qc_rsd_file
            ), shell=True, check=True)

            # plot (a limited number of) compounds
            for compound in compounds:
                run("{} plot_compound --qc-corrected-file={} --compound={} --plot-location={}".format(
                    command_prefix,
                    qc_corrected_file,
                    compound,
                    plot_location
                ), shell=True, check=True)

        except:
            return False

        return True

if __name__ == '__main__':
    fire.Fire(Qcli)