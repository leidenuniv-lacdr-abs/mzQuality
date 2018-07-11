# mzQuality

[![Build Status](https://travis-ci.org/leidenuniv-lacdr-abs/mzQuality.svg?branch=master)](https://travis-ci.org/leidenuniv-lacdr-abs/mzQuality) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/3de83824a5a14684b69d9c00719ca029)](https://www.codacy.com/app/michaelvanvliet/mzQuality?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=leidenuniv-lacdr-abs/mzQuality&amp;utm_campaign=Badge_Grade)

### Tool for quality monitoring and reporting of mass spectrometry measurements


#### Supported methods

1) Measurement summary  
  This method shows a summary of the number of metabolites and samples measured and in how many batches these were measured.  
  
2) Blank effect  
  What is the signal in the blank samples? i.e. empty vials. This measures the signal of the background.  
  
3) Retention time shifts (rt_shifts)  
  What is the variation of the retention time per metabolite and batch? This is used to ensure that the right compound was chosen and acts as a quality control tool. Some variation or drift is expected, but outliers indicate that a different compound was accidentally chosen.   
  
4) Quality control correction (qc_correction)  
  The quality control (QC) samples included in the run are used to correct for between batch variation. All QCs have the same concentrations, so they can be used for batch correction.

5) RSD of QC (rsd_qc)  
  This reports the relative standard deviation (RSD) of the QC samples. The denominator of the RSD is the absolute value of the mean, so the RSD will always be positive.  
  
6) RSD of replicates (rsd_replicates)  
 This reports the relative standard deviation (RSD) of replicated samples. Replicated samples are included to assess drift of the mass spec during a batch. The denominator of the RSD is the absolute value of the mean, so the RSD will always be positive.  
  
7) RSD of internal standards (rsd_is)  
 This reports the relative standard deviation (RSD) of internal standards. The internal standards are used to calculate the reported ratio of a compound; also called the internal standard corrected intensity. The denominator of the RSD is the absolute value of the mean, so the RSD will always be positive.
  
8) Plot the information of compound(s)  
  This provides a plot showing the uncorrected area per compound, the internal standard and qc corrected ratio per compound and the retention time per compound. These plots allow the assessment of quality per project.  

9) Export results as samples vs. compounds  
  A dataframe of samples (rows) vs. compounds (columns) is exported as a tab separated file.
 

For more background information, please read the following publication: [Analytical Error Reduction Using Single Point Calibration for Accurate and Precise Metabolomic Phenotyping](https://doi.org/10.1021/pr900499r) by Frans vd Kloet  

## Getting started

## How to contribute
If you have contributions please send a PR ([pull request](https://help.github.com/articles/about-pull-requests/)) with the correction(s) or improvement(s), and notify one of the developers to review it.
