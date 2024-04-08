# declutter-mri-protocols
Python tools to find differences in Siemens protocol trees and sequence parameters. 

[![DOI](https://zenodo.org/badge/638967134.svg)](https://zenodo.org/doi/10.5281/zenodo.10940450)

## Requirements

run `$ pip install -r requirements.txt` 

or install manually:

- dictdiffer `$ pip install dictdiffer` 
- xlsxwriter `$ pip install xlsxwriter`
- pandas `$ pip install pandas`
- xmldiff `$ pip install xmldiff`
- openpyxl `$ pip install openpyxl`

## Usage

![image](https://github.com/GIfMI/declutter-mri-protocols/assets/15831740/22347ca2-0318-4e09-816e-36e64ba3c5c5)


## Reference

When using the tools, please cite the following paper: Pullens, P. et al. Declutter the MRI protocol tree: Managing and comparing sequence parameters of multiple clinical Siemens MRI systems. Physica Medica 120, 103342 (2024) [https://doi.org/10.1016/j.ejmp.2024.103342](https://doi.org/10.1016/j.ejmp.2024.103342).

## Acknowledgement

These tools use the following packages/libraries next to the standard Python libraries:

- xlsxwriter [https://xlsxwriter.readthedocs.io/](https://xlsxwriter.readthedocs.io/). XlsxWriter was written by John McNamara.
- dictdiffer [https://dictdiffer.readthedocs.io](https://dictdiffer.readthedocs.io). Dictdiffer was originally developed by Fatih Erikli. It is now being developed and maintained by the Invenio collaboration. 
