#!/usr/bin/env python2

import argparse
from sys import exit
from array import array
import ROOT

# TODO: There are several sanity checks that could be implemented, to make sure
#       the passed arguments are correct

def get_table_values(table):
    m = []
    xs = []
    unc = []
    with open(table, 'r') as f:
        for line in f:
            m.append(float(line.split()[0]))
            xs.append(float(line.split()[1]))
            unc.append(float(line.split()[2]))
    return m, xs, unc

if __name__ == '__main__':

    # Don't let ROOT take over the command line options, that are intended for
    # python (keeps preserving the helptext from argparse)
    ROOT.PyConfig.IgnoreCommandLineOptions = True

    # Parse options
    helptext= '''
    Plot cross section tables that have been generated with harvest_resummino.
    Cross section tables can be added as numerator or denominator. This has
    only an effect on the ratio plots. If there is no denominator table, no
    ratio plot is shown. If there is a denominator table, all other tables will
    be divided against it in the ratio plot. There can only be one denominator
    table.
    '''
    parser = argparse.ArgumentParser(description=helptext, add_help=True)
    parser.add_argument('-d', action='store', dest='den', help='Denominator table')
    parser.add_argument('-n', action='append', dest='num', help='Numerator table', default=[])
    parser.add_argument('-l', action='append', dest='leg', help='Legend entry for tables (denominator first)', default=[])
    parser.add_argument('-t', action='store', dest='title', help='Title of histogram', default='')
    parser.add_argument('-o', action='store', dest='outname', help='Output name of pdf file', default='name')
    args = parser.parse_args()

    if (not args.num):
        print 'Please define at least one table for the numerator.'
        print 'Exit.'
        exit()

    # Get values from the tables
    if (args.den):
        den_m, den_xs, den_unc = get_table_values(args.den)
        den_name = args.den
    num_m = []
    num_xs = []
    num_unc = []
    num_name = []
    for num in args.num:
        m, xs, unc = get_table_values(num)
        num_m.append(m)
        num_xs.append(xs)
        num_unc.append(unc)
        num_name.append(num)

    # Define canvas and sub-pads
    c = ROOT.TCanvas()
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetTitleFontSize(.06)
    y_pad = .4 if (args.den) else .1
    p1 = ROOT.TPad("pad1", "pad1", 0., y_pad, 1., 1.)
    p2 = ROOT.TPad("pad2", "pad2", 0., .0, 1., y_pad)
    p1.SetLeftMargin(.13)
    p2.SetLeftMargin(.13)
    p1.SetTicks(1, 1)
    p2.SetTicks(1, 1)
    p1.SetTopMargin(.12)
    p1.SetBottomMargin(0.01)
    p2.SetBottomMargin(.31)
    p1.Draw()
    p2.Draw()

    # Fill histograms for denominator table
    hs = []
    h_ratios = []
    if (args.den):
        dm = den_m[1]-den_m[0]
        try:
            hname = args.leg[0]
        except IndexError:
            hname = den_name
        h = ROOT.TH1D(hname, args.title, len(den_m), den_m[0]-dm/2, den_m[-1]+dm/2)
        for idx2 in range(len(den_m)):
            m = den_m[idx2]
            xs = den_xs[idx2]
            unc = den_unc[idx2]
            h.SetBinContent(h.FindBin(m), xs)
            h.SetBinError(h.FindBin(m), unc)

        # Fill ratio histogram (trivially 1 here)
        h_ratio = h.Clone()
        h_ratio.Divide(h)
        h_ratio.SetTitle('')

        hs.append(h)
        h_ratios.append(h_ratio)

    # Fill histograms for numerator tables
    for idx1 in range(len(num_m)):
        dm = num_m[idx1][1]-num_m[idx1][0]
        try:
            # Shifted by one since the denominator comes first
            hname = args.leg[idx1+1]
        except IndexError:
            hname = num_name[idx1]
        h = ROOT.TH1D(hname, args.title, len(num_m[idx1]), num_m[idx1][0]-dm/2, num_m[idx1][-1]+dm/2)
        for idx2 in range(len(num_m[idx1])):

            # Fill main histograms
            m = num_m[idx1][idx2]
            xs = num_xs[idx1][idx2]
            unc = num_unc[idx1][idx2]
            h.SetBinContent(h.FindBin(m), xs)
            h.SetBinError(h.FindBin(m), unc)

        hs.append(h)

        # Fill ratio histograms
        if (args.den):
            h_ratio = h.Clone()
            # Divide by first entry of hs, which is the denominator histogram
            # (if args.den is True)
            h_ratio.Divide(hs[0])
            h_ratio.SetTitle('')
            h_ratios.append(h_ratio)

    # Get min and max of histograms to later scale them accordingly
    h_max = 0
    h_min = 99999
    h_ratio_max = 0
    h_ratio_min = 99999
    # Style histogram
    for idx, h in enumerate(hs):
        # Skip black, white and yellow
        h.SetLineColor(idx+2 if idx<3 else idx+3)
        h.SetLineWidth(2)
        h.GetXaxis().SetLabelSize(.0)
        h.GetYaxis().SetLabelSize(.066)
        h.GetYaxis().SetTitleSize(.082)
        h.GetYaxis().SetTitleOffset(.69)
        h.GetXaxis().SetTickSize(.03)
        h.GetYaxis().SetTitle('#sigma [fb]')
        h_max = max(h.GetMaximum(), h_max)
        h_min = min(h.GetMinimum(), h_min)
    hs[0].GetYaxis().SetRangeUser(h_min/2., 2.*h_max)
    for idx, h in enumerate(h_ratios):
        # Skip black, white and yellow
        h.SetLineColor(idx+2 if idx<3 else idx+3)
        h.SetLineWidth(2)
        h.GetXaxis().SetLabelSize(.096)
        h.GetYaxis().SetLabelSize(.096)
        h.GetYaxis().SetTitleSize(.107)
        h.GetXaxis().SetTitleSize(.111)
        h.GetYaxis().SetTitleOffset(.52)
        h.GetXaxis().SetTickSize(.046)
        h.GetXaxis().SetTitle('m_{#tilde{#chi}}')
        h.GetYaxis().SetTitle('ratio w.r.t. {}'.format(hs[0].GetName()))
        h_ratio_max = max(h.GetMaximum(), h_ratio_max)
        h_ratio_min = min(h.GetMinimum(), h_ratio_min)

    # Set range shown on ratio histogram, if available
    try:
        h_ratios[0].GetYaxis().SetRangeUser(.9*h_ratio_min, 1.1*h_ratio_max)
    except IndexError:
        pass

    # Legend
    l = ROOT.TLegend(.72, .83-len(hs)*.11, .86, .83)
    l.SetTextAlign(32)
    l.SetTextSize(.07)
    l.SetBorderSize(0)
    for h in hs:
        l.AddEntry(h, h.GetName(), 'L')

    # Draw and save histogram
    p1.cd()
    same=''
    for h in hs:
        h.Draw('HIST C {}'.format(same))
        same = 'SAME'
    p1.SetLogy()
    l.Draw()
    p2.cd()
    same=''
    for h in h_ratios:
        h.Draw('HIST C {}'.format(same))
        same = 'SAME'
    for ext in ['pdf', 'png']:
        c.Print('{}.{}'.format(args.outname, ext))
