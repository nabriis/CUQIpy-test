#!/usr/bin/env python
# Basic packages
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

# Add CUQIpy (assumed to be in ../cuqipy/)
import sys
sys.path.append("../cuqipy/")
import cuqi

# Add PySimpeGUI
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Convenience method to draw figure
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def make_callback_function(fig, fig_agg, TP, Ns):
    """ Method to create a callback function that gets called by CUQIpy for each sample

    Parameters
    ----------
    fig : matplotlib figure
        Figure to plot progress in
    
    fig_agg : matplotlib figure
        Figure to draw in GUI

    TP : cuqi.testproblem.TestProblem
        Test problem that is sampled from (used to get parameters)

    Ns : int
        Number of samples to draw

    Returns
    -------
    callback : function
        Callback function that we feed to CUQIpy
    
    Notes
    -----
    The current implementation stores the samples in a NumPy array and periodically creates a CUQI samples object and plots the CI.

    """

    # Preallocate samples array to compute statistics along the way
    # TODO: In future versions of CUQIpy we can access the samples object directly in the callback function
    samples = np.zeros((TP.model.domain_dim, Ns))

    # Create callback method that we want CUQIpy to call. It must have structure (sample, n).
    def callback(sample, n):

        # Store current sample in array
        samples[:, n-1] = sample

        # Plot ci every x samples
        if n % 50 == 0:

            fig.clear()

            # Create samples object with samples 0:n and plot ci
            cuqi.samples.Samples(samples[:,:n]).plot_ci(exact=TP.exactSolution)
            plt.ylim([-0.5,1.5])
            plt.title(f"Samples 1:{n}")
            
            # Draw plot in GUI
            fig_agg.draw()

    return callback #We return the callback function so we can feed it to CUQIpy

# Main method
def main():

    # Define the GUI layout
    layout = [[sg.Text('CUQIpy interactive demo', size=(40, 1), justification='center', font='Helvetica 20')],
              [sg.Canvas(size=(640, 480), key='-CANVAS-')],
              [sg.Text('Laplace_diff prior scale')],
              [sg.Slider(range=(0.0001, 0.1), default_value=0.01, resolution=0.0001, size=(40, 10), orientation='h', key='-SLIDER-DATAPOINTS-')],
              [sg.Button('Update', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')],
              [sg.Button('Exit', size=(10, 1), pad=((280, 0), 3), font='Helvetica 14')]]

    # Create the GUI and show it without the plot
    window = sg.Window('CUQIpy interactive demo', layout, finalize=True)

    # Extract canvas element to attach plot to
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    # Draw the initial figure in the window
    fig = plt.figure(figsize=(6.4,4.8))
    fig_agg = draw_figure(canvas, fig)

    while True:

        # Read current events and values from GUI
        event, values = window.read()

        # Clicked exit button
        if event in ('Exit', None):
            exit()

        # Clicked update button
        if event in ('Update', None):

            # Get values from slider input
            scale = float(values['-SLIDER-DATAPOINTS-']) # scale

            # Number of samples
            Ns = 500

            # Define test problem and prior
            TP = cuqi.testproblem.Deconvolution1D(phantom="square") # Default values
            TP.prior = cuqi.distribution.Laplace_diff(np.zeros(TP.model.domain_dim), scale) # Set prior

            # Create callback function for progress plotting (Burn-in is 20% by default so we allocate 120% of samples)
            callback = make_callback_function(fig, fig_agg, TP, int(1.2*Ns))

            # Sample posterior
            xs = TP.sample_posterior(Ns, callback=callback)

            # Update plot
            fig.clear()
            xs.plot_ci(95, exact=TP.exactSolution)
            plt.ylim([-0.5,1.5])
            
            # Draw plot in GUI
            fig_agg.draw()
            
            # Print update in console
            print(" Figure updated!")

if __name__ == '__main__':
    sg.change_look_and_feel('Reddit') #Theme
    main() #Runs main method
