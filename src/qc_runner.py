import os
from lib.mea import Mea
from lib.qccalc import Qccalc
from lib.qcplot import Qcplot

# init Mea object (with data)
base_folder = '../data/'
plot_folder = '../data/plots'
mea = Mea(mea_file=base_folder + 'combined.tsv')

print("Script execution from {}".format(os.getcwd()))
print("Data folder {}".format(base_folder))
print("Batches: {}".format(len(mea.get_batches())))
print("Samples: {}".format(len(mea.get_samples())))
print("Compounds: {}".format(len(mea.get_compounds())))

# init QC Calculations object
qccalc = Qccalc(mea=mea)
qcplot = Qcplot(mea=mea)

# do blank effect calculations
if True:
    blank_effect = qccalc.blank_effect()
    blank_effect.to_csv(base_folder + 'blank_effect.tsv', sep="\t", index=False, encoding='utf-8')
    print("Blank effect reported")

# do qc correction
if True:
    qc_corrected = qccalc.qc_correction()
    qc_corrected.to_csv(base_folder + 'qc_corrected.tsv', sep="\t", index=False, encoding='utf-8')
    print("QC Corrected data reported")

    # init QC Calculations object
    mea.set_measurements(qc_corrected)
    qccalc = Qccalc(mea=mea)

    mea.as_table(column='qc_corrected', location=base_folder + 'qc_intra.tsv', include_is=False)
    mea.as_table(column='inter_median_qc_corrected', location=base_folder + 'qc_inter.tsv', include_is=False)
    print("QC corrected inter batch data exported")

# calculate RSD_QC's
if True:
    rsdqc = qccalc.rsdqc()
    rsdqc.to_csv(base_folder + 'rsdqc.tsv', sep="\t", index=False, encoding='utf-8')
    print("RSDqc's done")

# calculate RT shifts
if True:
    rt_shifts = qccalc.rt_shifts()
    rt_shifts.to_csv(base_folder + 'rt_shifts.tsv', sep="\t", index=False, encoding='utf-8')
    print("RT shifts calculated")

# save sample vs feature
if True:
    mea.as_table(column='area', location=base_folder + 'area.tsv', include_is=True)
    mea.as_table(column='ratio', location=base_folder + 'ratio.tsv', include_is=False)
    print("Exported area and ratio")

# plot compounds data
if True:
    mea = Mea(mea_file=base_folder + 'qc_corrected.tsv')
    qcplot = Qcplot(mea=mea)

    for compound in mea.get_compounds():
        qcplot.plot_compound_qc_data(
            compound=compound,
            location=plot_folder
        )
