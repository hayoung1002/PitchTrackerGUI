import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter

import numpy as np
from numpy.lib.stride_tricks import as_strided

import Tkinter as tk  # python 2.7
import ttk            # python 2.7
import sys
import Tkinter, Tkconstants, tkFileDialog
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter

from scipy.io import wavfile

import pYINmain
from YinUtil import RMS

import pygame
import pygame.mixer

f_s = 44100
frameSize = 2048
hopSize = 256
filename = ''

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)

        self.createWidgets()

    def createWidgets(self):
        fig=plt.figure(figsize=(9,9))


        a = fig.add_subplot(211)
        a.set_xlabel('Time [sec]')
        a.set_ylabel('Normalized Amplitude')
        a.set_title('Audio File')
        
        b = fig.add_subplot(212)

        b.set_title('Pitch Contour')
        b.set_yscale('log', basey = 2)
        b.set_xlabel('Time [sec]')

        b.set_ylabel('Pitch [MIDI]')
       
        b.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        

        plt.autoscale(tight=True)
        
        canvas=FigureCanvasTkAgg(fig,master=root)
        canvas.get_tk_widget().grid(row=2,column=2)
        canvas.show()

        self.plotbutton = tk.Button(master=root, text = "Open File", command=lambda: self.plot(canvas,a,b))
        self.plotbutton.grid(row=0,column=0 )
        
        self.playbutton = tk.Button(master=root, text = "Play Music", command=lambda: self.playMusic())
        self.playbutton.grid(row=1,column=0)
        
    def playMusic(self):
        print(filename)
        pygame.mixer.init(44100, -16,2,2048)
        pygame.mixer.music.load(filename)

        pygame.mixer.music.play()
    
        #self.plotbutton=tk.Button(master=root, text="plot", command=lambda: self.plot(canvas,a,b))

        #self.plotbutton.grid(row=0,column=0)


    def plot(self,canvas,a,b):
        global filename 
        filename = tkFileDialog.askopenfilename() 
        f_s, afAudioData = wavfile.read(filename)
        afAudioData = afAudioData.astype(np.float) 
        #convert to float

        # Normalizing and Downsizing File
        if (len(afAudioData.shape) > 1):
            afAudioData = afAudioData.mean(axis = 1)
        if (len(afAudioData) > 1):
            afAudioData = afAudioData/max(abs(afAudioData))

        c = ['r','b','g']  # plot marker colors
        a.clear()         # clear axes from previous plot
        
        
        a.plot((np.arange(0,len(afAudioData)).astype(float))/f_s, afAudioData)
        
        
        
        # create pYIN Object
        pYinInst = pYINmain.PyinMain()
        pYinInst.initialise(channels = 1, inputSampleRate = f_s, stepSize = hopSize, blockSize = frameSize, lowAmp = 0.25, onsetSensitivity = 0.7, pruneThresh = 0.1)

        fstart_vec = np.array(range(0,len(afAudioData)-frameSize, hopSize))

        for fstart in fstart_vec:
            if fstart+frameSize <= len(afAudioData):
                frame = afAudioData[fstart:fstart+frameSize]
            else:
                frame = afAudioData[fstart:end]
            fs = pYinInst.process(frame)

        


        monoPitch = pYinInst.getSmoothedPitchTrack()

        pitches = []

        for ii in fs.m_oSmoothedPitchTrack:
            pitches = np.concatenate((pitches,ii.values), axis=0)

        p = 69 + 12 * np.log2(abs(pitches)/440)

        x = fstart_vec.astype(float)/float(f_s)
        b.plot(x,p)
        # b.yticks(np.arange(min(pitches), max(pitches)+1, 1.0))
        #b.yaxis.set_major_locator(plt.MaxNLocator(3))

        canvas.draw()

root=tk.Tk()
root.wm_title("Pitch Contour")
app=Application(master=root)
app.mainloop()
