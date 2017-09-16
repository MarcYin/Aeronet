from glob import glob
import pandas as pd
from scipy.interpolate import interp1d
import pylab as plt
from scipy.stats import linregress
import numpy as np

def read_aeronet(filename):
    """Read a given AERONET AOT data file, and return it as a dataframe.
    
    This returns a DataFrame containing the AERONET data, with the index
    set to the timestamp of the AERONET observations. Rows or columns
    consisting entirely of missing data are removed. All other columns
    are left as-is.
    from http://blog.rtwilson.com/reading-aeronet-data-in-pandas-a-simple-helper-function/
    """
    dateparse = lambda x: pd.datetime.strptime(x, "%d:%m:%Y %H:%M:%S")
    aeronet = pd.read_csv(filename, skiprows=4, na_values=['N/A'],
                          parse_dates={'times':[0,1]},
                          date_parser=dateparse)

    aeronet = aeronet.set_index('times')
    del aeronet['Julian_Day']
    
    # Drop any rows that are all NaN and any cols that are all NaN
    # & then sort by the index
    an = (aeronet.dropna(axis=1, how='all')
                .dropna(axis=0, how='all')
                .rename(columns={'Last_Processing_Date(dd/mm/yyyy)': 'Last_Processing_Date'})
                .sort_index())

    return an

def inter_aot(wv, aot, full=False, Second=True):
    '''
    A function for the interpolation of Aeronet measurements 
    to AOT 550.
    args:
    wv -- wavelength 
    aot -- corresponding aot value for each wavelength
    full -- full out put or not
    Second -- second order fitting
    return:
    if full = True
    aot_550, ang, off, cov, error, correlation are returned
    if full = False
    only aot_550 and the Angustrom and offset are returned
    '''
    m = (wv>=400) & (wv<=870)
    if Second:
        a1,a2,a3 = np.polyfit(np.log(wv[m]), -1*np.log(aot[m]), 2)
        p = np.poly1d(np.polyfit(np.log(wv[m]), -1*np.log(aot[m]), 2))
        error = [sum(((p(np.log(wv[m]))-(-1*np.log(aot[m])))**2)),]
        aot_550 = np.exp(-1*p(np.log(550)))
    else:   
        ang, off, r_value, p_value, std_err = linregress(np.log(wv[m]), -1*np.log(aot[m]))
        p = np.poly1d([ang, off])
        error = [std_err, r_value, p_value ]                
        aot_550 = np.exp(-1*(ang*np.log(550)+off))
    if full:
        return aot_550, p, error
    else:
        return aot_550, p

def Aeronet_measures(site, date, time,  plot_all=0, plot_date=0, plot_ang=0, root = None):
    '''
    A function for the retrieval of aeronet measurements
    at specific date and time from an Aeroent site
    linear interpolation used for the interpolation
    over time of the aot and corresponding Triple values
    A fitting to Angstrom is used for the AOT 550 instead 
    of 1st or 2nd order polynominal fitting
    
    args:
    site -- Aeronet site names
    date -- date in the format of 'yyyy-mm-dd'
    time -- float vlaue of time in a day, like '23.56'
    plot_all -- plot both the Aeronet measurements of the day and Angstrom fitting 
    root -- directory to the aeronet measurements files downloaded from 
    'https://aeronet.gsfc.nasa.gov/new_web/index.html'
    
    return:
    aero_date -- aeronet measurements of the day
    err -- Triple error
    aot_550 -- aot_550 at the time
    (ang, off) -- Angstrom and fitting off set
    
    '''
    fname = glob(root+'*%s*'%site)[0]
    aero = read_aeronet(fname)
    keys = aero[date].keys()
    aero_date = aero[date].loc[:,keys[0]:'AOT_340'].dropna(axis=1, how='all').dropna(axis=0, how='all')
    err = aero[date].loc[:,'%TripletVar_'+keys[0].split('_')[-1]:'%TripletVar_340'].dropna(axis=1, how='all').dropna(axis=0, how='all')
    #Angstrom_440_870 = aero[date].loc[:,'440-870Angstrom']
    hours = np.array([i.hour+ i.minute/60. + i.second/3600. for i in aero_date.index])
    f_aot = interp1d(hours, aero_date.T, bounds_error=0)
    f_err = interp1d(hours, err.T, bounds_error=0)
    #f_ang = interp1d(hours, Angstrom_440_870.T, bounds_error=0)
    wv = np.array([int(i.split('_')[-1]) for i in aero_date.keys()])
    ynew = f_aot(time)
    enew = f_err(time)
    aot_550_1, p1, error_1 = inter_aot(wv, ynew, full=1, Second=0)
    aot_550_2, p2, error_2 = inter_aot(wv, ynew, full=1, Second=1)
    if plot_all | plot_date:
        plt.figure(figsize=(12,6))
        for i,_ in enumerate(aero_date.keys()):
            plt.errorbar(aero_date.index, aero_date[aero_date.keys()[i]],ls='--',marker='o', ms=1,
                         yerr= 0.01*err[err.keys()[i]],capsize=3, elinewidth=0.5,lw=0.5,
                         markeredgewidth=0.5, label=aero_date.keys()[i])
        tickes = pd.DatetimeIndex([date+' %02d:00:00'%i for i in np.arange(0,24.,3)])
        ticks = ['%02d:00:00'%i for i in np.arange(0,24., 3)]
        plt.xticks(tickes, ticks, rotation=45)
        plt.xlim(tickes[0], pd.DatetimeIndex([date+' 23:59:59']))
        plt.legend()
        plt.title('%s    %s    Level 2 AOT'%(site, date))
        plt.ylabel('AOT')
        
    if plot_all | plot_ang:
        fig = plt.figure(figsize=(12,6))
        ax = fig.add_subplot(111)
        ax.errorbar(wv, ynew,enew*0.01, label='Aeronets', ls='--',marker='o', ms=2,
                        capsize=2, elinewidth=0.5,ecolor='r',c='k',lw=0.5,
                         markeredgewidth=0.5)
        ang_aot_1 = np.exp(-1*p1(np.log(np.arange(wv.min(), wv.max()+1, 1))))
        ang_aot_2 = np.exp(-1*p2(np.log(np.arange(wv.min(), wv.max()+1, 1))))
        ax.plot(np.arange(wv.min(), wv.max()+1, 1), ang_aot_1, '--', label='1st order Fiiting')
        ax.plot(np.arange(wv.min(), wv.max()+1, 1), ang_aot_2, '--', label='2nd order Fiiting')
        ax.plot(550, aot_550_1 , 'o', label='1st order AOT 550')
        ax.plot(550, aot_550_2 , 'o', label='2nd order AOT 550')
        ax.annotate('1st oder fitting AOT 550 = %.03f'%aot_550_1, xy=(550, aot_550_1),  xycoords='data',
                    xytext=(0.5, 0.75), textcoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                    horizontalalignment='left', verticalalignment='top',
                    )
        ax.annotate('2nd oder fitting AOT 550 = %.03f'%aot_550_2, xy=(550, aot_550_2),  xycoords='data',
                    xytext=(0.5, 0.55), textcoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                    horizontalalignment='left', verticalalignment='top',
                    )
        plt.legend()
        plt.ylabel('AOT')
        plt.xlabel('Wavelength ($nm$)')
        plt.title('AOT at %02d:%02d:%02d'%(int(time), (time-int(time))*60, ((time - int(time))*60.-int((time-int(time))*60))*60))
    return [aot_550_2, p2, error_2], [aot_550_1, p1, error_1]