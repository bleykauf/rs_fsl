import pyvisa as visa
import numpy as np
import pandas as pd


def read_csv(filename):
    """Reads x and y values measured by the spectrum analyzer stored in a csv file."""

    data = pd.read_csv(
        filename, delimiter=";", skiprows=28, usecols=[0, 1], names=["x", "y"]
    )
    x, y = data.x.values, data.y.values
    return x, y


def _to_numeric(string):
    """Converts strings received from instrument to numerical values."""
    string = string.rstrip()
    arr = np.fromstring(string, sep=",")
    if len(arr) > 1:
        return arr
    else:
        return arr[0]  # no array for single values


class FSL:
    def __init__(self, ip, announce_connection=False):
        """
        Communication with the Rohde&Schwarz FSL spectrum analyzer via pyvisa. The IP
        address can be found from the R&S FSL by pressing Setup, General Setup, Network
        Address, IP Address and can be directly be specified with the `ip`
        keyword.
        """
        addr = "TCPIP0::{}::inst0::INSTR".format(ip)
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(addr)
        if announce_connection:
            print("Successfully connected to {}".format(self.idn()))

    # basic communication with device --------------------------------------------------

    def idn(self):
        """Identification of instrument."""
        return self.instr.query("*IDN?").rstrip()

    def clear(self):
        """Reset status register"""
        self.instr.write("*CLS")

    def reset(self):
        """Reset instrument"""
        self.instr.write("*RST")

    # Set and get basic instrument settings --------------------------------------------

    @property
    def freq_span(self):
        """Frequency span in Hertz"""
        return _to_numeric(self.instr.query("FREQ:SPAN?"))

    @freq_span.setter
    def freq_span(self, value):
        self.instr.write("FREQ:SPAN {}".format(value))

    @property
    def freq_center(self):
        """Center frequency"""
        return _to_numeric(self.instr.query("FREQ:CENT?"))

    @freq_center.setter
    def freq_center(self, value):
        self.instr.write("FREQ:CENT {}".format(value))

    @property
    def freq_start(self):
        """Start frequency in Hertz"""
        return _to_numeric(self.instr.query("FREQ:STAR?"))

    @freq_start.setter
    def freq_start(self, value):
        self.instr.write("FREQ:STAR {}".format(value))

    @property
    def freq_stop(self):
        """Start frequency Hertz"""
        return _to_numeric(self.instr.query("FREQ:STOP?"))

    @freq_stop.setter
    def freq_stop(self, value):
        self.instr.write("FREQ:STOP {}".format(value))

    @property
    def attenuation(self):
        """Attenuation in dB"""
        return _to_numeric(self.instr.query("INP:ATT?"))

    @attenuation.setter
    def attenuation(self, value):
        self.instr.write("INP:ATT {}".format(value))

    @property
    def rbw(self):
        """resolution bandwidth in Hertz"""
        return _to_numeric(self.instr.query("BAND:RES?"))

    @rbw.setter
    def rbw(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.instr.write("BAND:AUTO ON")
        else:
            self.instr.write("BAND:RES {}".format(value))

    @property
    def vbw(self):
        """video bandwidth in Hertz"""
        return _to_numeric(self.instr.query("BAND:VID?"))

    @vbw.setter
    def vbw(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.instr.write("BAND:VID:AUTO ON")
        else:
            self.instr.write("BAND:VID {}".format(value))

    @property
    def sweep_time(self):
        """Sweep time in seconds"""
        return _to_numeric(self.instr.query("SWE:TIME?"))

    @sweep_time.setter
    def sweep_time(self, value):
        if type(value) is str and value.upper() == "AUTO":
            self.instr.write("SWE:TIME:AUTO ON")
        else:
            self.instr.write("BAND:RES {}".format(value))
        self.instr.write("SWE:TIME {}".format(value))

    # Sweeping -------------------------------------------------------------------------

    @property
    def continuous_sweep(self):
        """Continuous (True) or single sweep (False)"""
        return bool(_to_numeric(self.instr.query("INIT:CONT?")))

    @continuous_sweep.setter
    def continuous_sweep(self, on):
        if on:
            self.instr.write("INIT:CONT ON")
        else:
            self.instr.write("INIT:CONT OFF")

    def single_sweep(self):
        """Performas a sweep with sync."""
        self.instr.write("INIT; *WAI")

    def continue_single_sweep(self):
        """Continues with single sweep with sync."""
        self.instr.write("INIT:CONM; *WAI")

    # Traces ---------------------------------------------------------------------------

    def read_trace(self):
        """Read trace data, returns x (frequency) and y (level)"""
        y = _to_numeric(self.instr.query("TRAC1? TRACE1"))
        n = len(y)  # numer of trace points
        x = np.linspace(self.freq_start, self.freq_stop, n)
        return x, y

    @property
    def trace_mode(self):
        return self.instr.query("DISP:TRAC:MODE?").rstrip()

    @trace_mode.setter
    def trace_mode(self, mode):
        _modes = ["WRIT", "MAXH", "MINH", "AVER", "VIEW"]
        if mode.upper() not in _modes:
            raise KeyError("mode has to be in {}".format(_modes))
        else:
            self.instr.write("DISP:TRAC:MODE {}".format(mode))

    # Markers --------------------------------------------------------------------------

    def create_marker(self, num=1, is_delta_marker=False):
        """
        The number of the marker (default 1) and a bool to define whether the
        marker is a delta marker (default False).
        """
        return self.Marker(self, num, is_delta_marker)

    class Marker:
        def __init__(self, device, num, is_delta_marker):
            """
            Marker and Delte Marker class. Specify device (instance of FSL), the marker
            number (int) and whether the marker is a delta marker (bool).
            """
            self.instr = device.instr
            self.is_delta_marker = is_delta_marker
            # building the marker name for the commands
            if self.is_delta_marker:
                # smallest delta marker number is 2
                self.name = "DELT" + str(max(2, num))
            else:
                self.name = "MARK"
                if num > 1:
                    # marker 1 doesn't get a number
                    self.name = self.name + str(num)

            self.activate()

        def activate(self):
            """Activate a marker"""
            self.instr.write("CALC:{}:STAT ON".format(self.name))

        def disable(self):
            """Disable a marker"""
            self.instr.write("CALC:{}:STAT OFF".format(self.name))

        def to_trace(self, n_trace=1):
            """Set marker to trace (default 1)"""
            self.instr.write("CALC:{}:TRAC {}".format(self.name, n_trace))

        @property
        def peak_excursion(self):
            """Peak excursion in dB"""
            return _to_numeric(self.instr.query("CALC:{}:PEXC?".format(self.name)))

        @peak_excursion.setter
        def peak_excursion(self, value):
            self.instr.write("CALC:{}:PEXC {}".format(self.name, value))

        def to_peak(self):
            """Set marker to peak"""
            self.instr.write("CALC:{}:MAX".format(self.name))

        def to_next_peak(self, relative="right"):
            """Set marker to next peak (left or right of current position)"""
            self.instr.write("CALC:{}:MAX:{}".format(self.name, relative))

        @property
        def x(self):
            """Frequency in hertz"""
            return _to_numeric(self.instr.query("CALC:{}:X?".format(self.name)))

        @x.setter
        def x(self, value):
            self.instr.write("CALC:{}:X {}".format(self.name, value))

        @property
        def y(self):
            """Amplitude of the marker"""
            return _to_numeric(self.instr.query("CALC:{}:Y?".format(self.name)))

        @y.setter
        def y(self, value):
            self.instr.write("CALC:{}:Y {}".format(self.name, value))

        def zoom(self, value):
            """Zoom in two a frequency span or by a factor"""
            self.instr.write("CALC:{}:FUNC:ZOOM {}; *WAI".format(self.name, value))
