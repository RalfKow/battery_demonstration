# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 10:16:14 2020

GUI for battery demonstartion using real-time data from OPC UA

@author: hube
"""

# %% Import libraries

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from time import sleep
from matplotlib.widgets import Slider, Button
from opcuaclient_subscription import opcua, toggle

style.use('fivethirtyeight')
# %% Establish OPC UA connection

if __name__ == "__main__":

    opcua = opcua(user='BenjaminHuberEMPA', password='BenjaminHuberEMPA2020')

    try:
        
        opcua.connect()
        df_nodes = pd.DataFrame({'node':["ns=2;s=Gateway.PLC1.65NT-03032-D001.PLC1.MET51.strMET51Read.strWetterstation.strStation1.lrLufttemperatur",
                                         "ns=2;s=Gateway.PLC1.65NT-03032-D001.PLC1.MET51.strMET51Read.strWetterstation.strStation1.lrGlobalstrahlung"]})
        opcua.subscribe(df_Read=df_nodes)
        
        fig, ax = plt.subplots(2, 1)
        fig.set_size_inches (8.27, 5.5)
        fig.subplots_adjust(bottom=0.05, top=0.96, left=0.045, right=0.99, hspace=0.13)
        
        def animate(i):
            df = opcua.handler.df_Read
            df_temp = df.where(df['node'] == df_nodes.iloc[0, 0]).dropna()
            df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
            df_temp = df_temp.set_index('timestamp')
            df_temp.rename(columns={'value':'temp_amb'}, inplace=True)
            df_plot = df_temp[['temp_amb']].resample('1S').first()
            df_temp = df.where(df['node'] == df_nodes.iloc[1, 0]).dropna()
            df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
            df_temp = df_temp.set_index('timestamp')
            df_temp.rename(columns={'value':'irrad'}, inplace=True)
            df_plot = pd.concat([df_plot, df_temp[['irrad']].resample('1S').first()], axis=1)
            try:
                df_plot['temp_amb'].interpolate(method='linear', limit_directions='both', inplace=True)
                df_plot['irrad'].interpolate(method='linear', limit_directions='both', inplace=True)
            except:
                print("Not interpolated")
            
            ax[0].clear()
            ax[1].clear()
            
            ax[0].plot(df_plot["temp_amb"])
            ax[1].plot(df_plot["irrad"])
        
        ani = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()
        # %% Create GUI for battery handling

        # fig, ax = plt.subplots()
        # plt.subplots_adjust(top=0.985,
        #                     bottom=0.198,
        #                     left=0.047,
        #                     right=0.991,
        #                     hspace=0.2,
        #                     wspace=0.2)
        
        # P_0 = 0
        # dP_batt = 1
        # t = com['DFAB/371/temperature'].index
        # T = gaussian_filter(com['DFAB/371/temperature'].values, sigma=sigma_0)
        # l0 = plt.plot(t, com['DFAB/371/temperature'].values, label="$T_{\mathrm{raw}}$")
        # l, = plt.plot(t, T, lw=2, label="$T_{\mathrm{Gauss-filtered}}$")
        # ax.set_xlabel("Timestamp")
        # ax.set_ylabel("Temperature [°C]")
        # ax.legend(loc="upper right")
        # ax.margins(x=0)
        
        # axcolor = 'lightgoldenrodyellow'
        # axSigma = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
        
        # sSigma = Slider(axSigma, '$\sigma$', -100.0, 100.0, valinit=sigma_0, valstep=delta_sigma)
        
        
        # def update(val):
        #     sigma = sSigma.val
        #     l.set_ydata(gaussian_filter(com['DFAB/371/temperature'].values, sigma=sigma))
        #     fig.canvas.draw_idle()
        
        
        # sSigma.on_changed(update)
        
        # resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
        # button = Button(resetax, 'Reset', color=axcolor, hovercolor='0.975')
        
        
        # def reset(event):
        #     sSigma.reset()
        # button.on_clicked(reset)
        
        # figManager = plt.get_current_fig_manager()
        # figManager.window.showMaximized()
        
        # plt.show()

    finally:
        
        opcua.disconnect()
        print("OPC UA disconnected")
