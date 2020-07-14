################################################################################
# MIT LICENSE
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import collectd

from kmb_noc import kmb_probe_lookup
from flexnoc import *

PLUGIN_NAME = 'intel_ddr'  # Plugin name
PLUGIN_INSTANCE = 'mbw'  # plugin instance name
PLUGIN_TYPE = "memory_bandwidth"  # intel_ddr plugin type
PROBE_DSS = "dss"  # dss probe defined in kmb_noc.py
PROBE_SETUP_INTERVAL = 2  # Sleep used for 2sec after starting probe
COUNTER_0 = 0  # counter 0
COUNTER_2 = 2  # counter 2
DURATION = 0x1B  # 268 ms@500MHz or 191 ms@700MHz
CLK = 700000  # 700MHz as per Keembay_VPU_Databook 1.11
NO_OF_TRACE_PORTS = 6  # no of traceports used.


def intel_ddr_config(config):
    """ Reads the configuartions and apply its values to intel_ddr
    This method:
        - Reads the configuration from collectd.conf file, which are passed as arguments ad key & pair values.
        - Plugin interval is read and passed to plugin deamon here.
        - Collectd.register_read callback is called from here, as interval is sent as param. 
    :param config: This config contains key,value pair as read from colelctd.conf file.
    """
    for node in config.children:
        # Converting to lowercase as KEY accepts both "Lowercase & Uppercase".
        key = node.key.lower()
        val = node.values[0]
        if key == "interval":
            interval = int(val)  # setting Plugin interval as per collectd.conf
            collectd.info("Intel_DDR: setting interval %f" % interval)
        else:
            collectd.info("Intel_DDR : setting to global interval")
    # Calling Read function by passing interval
    collectd.register_read(intel_ddr_read, interval)


def intel_ddr_init():
    """ Initializes the intel_ddr plugin, only once.
    This method:
        - Caluclates the values to be divided for conversion to seconds.
        - Intitalizes the flexnoc_probe_init function in flexnox.py.
    """
    global sec
    sec = 2**DURATION / (CLK * 1000.0)  # convert CLK,duration to seconds
    flexnoc_probe_init(probe=PROBE_DSS, lookup=kmb_probe_lookup, logging=False)


def collectd_dispatch(plugin_instance, values, value_type):
    """ Dispatches the values to collectd deamon
    This method:
        - dispatches the intel_ddr values to collectd deamon read from intel_ddr_read.
    :param plugin_instance: reads the plugin instance form intel_ddr_read
    :param values: reads the plugin instance values form intel_ddr_read
    :param value_type: reads the plugin instance value type form intel_ddr_read
    """
    val = collectd.Values(plugin=PLUGIN_NAME)
    val.plugin_instance = plugin_instance
    val.type = value_type
    val.dispatch(values=[values])


def intel_ddr_read():
    """ Reads the values of ddr and calls the dispatch fucntion
    This method:
        - Reads the ddr values by setting up the probe, counters,traceports & then captures the values.
        - For capturing, uses other python files like - kmb_noc.py, flexnoc.py, ioremap.py
        - After capturing the values from ddr, calls the dispatch function.
    """
    try:
        sum = 0
        for tp in range(1, NO_OF_TRACE_PORTS + 1):
            rw_bytes_0 = 0  # bytes for counter 0
            rw_bytes_2 = 0  # bytes for counter 2
            flexnoc_counterp_setup(probe=PROBE_DSS,
                                   counter=COUNTER_0,
                                   trace_port=tp)
            flexnoc_counterp_setup(probe=PROBE_DSS,
                                   counter=COUNTER_2,
                                   trace_port=tp)
            flexnoc_probe_start(probe=PROBE_DSS)
            # 2sec of sleep is to write buffer into /dev/mem.
            time.sleep(PROBE_SETUP_INTERVAL)
            rw_bytes_0 = flexnoc_counterp_capture(probe=PROBE_DSS,
                                                  counter=COUNTER_0)
            rw_bytes_2 = flexnoc_counterp_capture(probe=PROBE_DSS,
                                                  counter=COUNTER_2)
            # calculating sum with rw_bytes_0, as rw_bytes_0 & bytes_2 are same
            sum = sum + (rw_bytes_0 / sec)
        collectd_dispatch("{}".format(PLUGIN_INSTANCE), sum, PLUGIN_TYPE)
    except:
        collectd.warning("Could not read MBTP values from %s" % PLUGIN_NAME)


collectd.register_config(intel_ddr_config)
collectd.register_init(intel_ddr_init)
