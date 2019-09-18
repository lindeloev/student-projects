# -*- coding: utf-8 -*-
"""
Helper functions for quadro N-back
"""


# Function that makes a rows*cols grid with cellsize=size for visual stimuli. Returns vertices for shapeStim and coordinates for stimulus.
def makeGrid(rows=3,cols=3, size=1):
    positions = []
    vertices = []
    xLength = size*cols
    yLength = size*rows
    
    # Draws the frame around the grid
    vertices.append((-0.5*xLength,-0.5*yLength))
    vertices.append(( 0.5*xLength,-0.5*yLength))
    vertices.append(( 0.5*xLength, 0.5*yLength))
    vertices.append((-0.5*xLength, 0.5*yLength))
    vertices.append((-0.5*xLength,-0.5*yLength))
    
    # Draws horizontal lines
    for row in range(1,rows):
        vertices.append((-0.5*xLength,size*row-0.5*yLength))
        vertices.append(( 0.5*xLength,size*row-0.5*yLength))
        vertices.append((-0.5*xLength,size*row-0.5*yLength))
    
    vertices.append((-0.5*xLength,-0.5*yLength))
    
    # Draws vertical lines
    for col in range(1,cols):
        vertices.append((size*col-0.5*xLength,-0.5*yLength))
        vertices.append((size*col-0.5*xLength, 0.5*yLength))
        vertices.append((size*col-0.5*xLength,-0.5*yLength))
    
    # Creates an array of positions
    for row in range(rows):
        for col in range(cols):
            positions.append((-0.5*xLength+0.5*size+size*col,-0.5*yLength+0.5*size+size*row))
    
    return {'vertices':vertices,'positions':positions}



def find_sublist(my_list, sublist):
    """ Joins the list elements to a string. 
    Then returns whether one contains the other (True/False)
    """
    my_string = ''.join([str(i) for i in my_list])
    substring = ''.join([str(i) for i in sublist])
    return(substring in my_string)
    


from scipy.stats import norm
import math
Z = norm.ppf

def SDT(hits, misses, fas, crs):
    """ returns a dict with d-prime measures given hits, misses, false alarms, and correct rejections"""
    # Floors an ceilings are replaced by half hits and half FA's
    half_hit = 0.5 / (hits + misses)
    half_fa = 0.5 / (fas + crs)
 
    # Calculate hit_rate and avoid d' infinity
    hit_rate = hits / (hits + misses)
    if hit_rate == 1: 
        hit_rate = 1 - half_hit
    if hit_rate == 0: 
        hit_rate = half_hit
 
    # Calculate false alarm rate and avoid d' infinity
    fa_rate = fas / (fas + crs)
    if fa_rate == 1: 
        fa_rate = 1 - half_fa
    if fa_rate == 0: 
        fa_rate = half_fa
 
    # Return d', beta, c and Ad'
    out = {}
    out['d'] = Z(hit_rate) - Z(fa_rate)
    out['beta'] = math.exp((Z(fa_rate)**2 - Z(hit_rate)**2) / 2)
    out['c'] = -(Z(hit_rate) + Z(fa_rate)) / 2
    out['Ad'] = norm.cdf(out['d'] / math.sqrt(2))
    
    return(out)