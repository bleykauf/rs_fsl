# RS FSL ‒ Python interface for the Rohde-Schwarz FSL Spectrum Analyzer

<!---
[![Conda](https://img.shields.io/conda/v/conda-forge/rs_fsl?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/rs_fsl)
[![Build Status](https://travis-ci.com/bleykauf/rs_fsl.svg?branch=main)](https://travis-ci.com/bleykauf/rs_fsl)
[![Documentation Status](https://readthedocs.org/projects/rs_fsl/badge/?version=latest)](https://rs_fsl.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/bleykauf/rs_fsl/badge.svg?branch=main)](https://coveralls.io/github/bleykauf/rs_fsl?branch=main)
-->
[![PyPI](https://img.shields.io/pypi/v/rs_fsl?color=blue)](https://pypi.org/project/rs_fsl/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Installation

To install `rs_fsl`, run

```
pip install rs_fsl
```


If you plan to make changes to the code, use

```
git clone https://github.com/bleykauf/rs_fsl.git
cd rs_fsl
pip install .
```
## Usage


```python
from rs_fsl import FSL
```

Connecting to the instrument. If the RS FSL is not connected to the phyics network, the address might be different and can be set manually with the `ip` keyword.


```python
fsl = FSL(ip='141.20.46.198')

Successfully connected to Rohde&Schwarz,FSL-18,100193/018,2.30
```

    
    


## Getting and setting parameters

Most parameters are implemented as properties in python, which means they can be read and written (getting and setting) in a consistent and simple way. If numerical values are provided, base units are used (seconds, hertz, decibel,...). 


```python
# Getting the current center frequency
fsl.freq_center

9000000000.0
```
    
```python

# Changing it to 10 MHz by providing the numerical value 
fsl.freq_center = 10e6
```


```python
# Verifying:
fsl.freq_center

10000000.0
```
    
```python
# Changing it to 1 GHz by providing a string and verifying the result
fsl.freq_center = '9GHz'
fsl.freq_center

9000000000.0
```

    

```python
# Setting the span to maximum
fsl.freq_span = '7GHz'
```

## Reading a trace

We will read the current trace


```python
x, y = fsl.read_trace()
```

## Markers

Markers are implemented as their own class. You can create them like this:


```python
m1 = fsl.create_marker()
```

Set peak exursion:


```python
m1.peak_excursion = 3
```

Set marker to a specific position:


```python
m1.x = 10e9
```

Find the next peak to the left and get the level:


```python
m1.to_next_peak('left')
m1.y

-34.9349060059

```







### Delta markers

Delta markers can be created by setting the appropriate keyword.


```python
d2 = fsl.create_marker(is_delta_marker=True)
d2.name

'DELT2'
```

## A example program

Program for measuring a beatnote


```python
m1 = fsl.create_marker() # create marker 1

# Set standard settings, set to full span
fsl.continuous_sweep = False
fsl.freq_span = '18 GHz'
fsl.rbw = "AUTO"
fsl.vbw = "AUTO"
fsl.sweep_time = "AUTO"

# Perform a sweep on full span, set the marker to the peak and some to that marker
fsl.single_sweep()
m1.to_peak()
m1.zoom('20 MHz')

# take data from the zoomed-in region
fsl.single_sweep()
x, y = fsl.read_trace()
```

## Authors

-   Bastian Leykauf (<https://github.com/bleykauf>)

## License

MIT License

Copyright © 2021 Bastian Leykauf

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
