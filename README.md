# CMS SUSY EWK Cross Sections

This package automatizes the process of calculating electroweak SUSY cross
sections for the CMS experiment at the CERN LHC and presenting them in a table
that is formatted for usage inside a Twiki. It consists of two parts:

## Condor

The condor part calculates the cross sections by using
[Resummino](https://www.resummino.org/). You can run
```bash
./condor_resummino_submit -h
```
to see all options. A typical job submission looks e.g. like this
```bash
./condor_resummino_submit -s wino.in -e 13 -p "1000023 1000024" -m "100 200 300"
```
which calculates the cross sections for a wino-like N2C1+ model at a
center-of-mass energy of 13 TeV, for degenerate N2 and C1+ masses of 100, 200
and 300 GeV.

You can also peek into `submitall` to see how to submit several jobs at once.

Also have a look at the two SLHA files provided, wino.in and hino.in, that
define the parameters of the model that cannot be controlled with the script.

The jobs run on HTCondor at the FNAL cluster. It has not been tested on other
sites, but e.g. CERN or DESY use HTCondor as well. While it is unlikely that
this package will run out of the box on these sites, there is likely not much
work involved to get it running there as well.

Your job output will be transferred to eos.

## Harvest

Once all your jobs completed successfully, you can harvest the output, with
```bash
./harvest_resummino /path/to/dir1 /path/to/dir2
```
You can add as many input directories as you want. For every input directory, a
Twiki formatted log file is created. All input directories in the end will be
merged into one log file, where the cross section of the different processes are
combined for a given mass.

Besides the Twiki format, simple text files ("tables") with the cross sections
are generated as well in the subdirectory "tables". These text files can be
plotted with `plot_xs.py`:
```bash
./plot_xs.py \
    -d tables/table1.txt \
    -n tables/table2.txt \
    -n tables/table3.txt \
    -l "#tilde{#chi}^{0}_{2} #tilde{#chi}^{#pm}_{1}" \
    -l "#tilde{#chi}^{+}_{1} #tilde{#chi}^{-}_{1}" \
    -l "#tilde{#chi}^{0}_{2} #tilde{#chi}^{0}_{1}" \
    -t "Higgsino cross sections"
```
Tables that are passed with the `-d` (denominator) or `-n` (numerator) flag are
plotted. If there is a denominator table, a ratio plotted will be added and the
numerator tables will be divided by the denominator table. The `-l` (legend)
flag defines the legend entries (denominator table first, if applicable, then
numerator tables in the order they have been declared). The `-t` (title) flag
defines the title of the plot.
