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

from ioremap import *
import time

probe_lookup = None
flexnoc_debug_en = None


def flexnoc_debug_log(s):
    if flexnoc_debug_en: print(s)
    return


def flexnoc_probe_init(probe, lookup, logging=False):
    global probe_lookup
    global flexnoc_debug_en
    probe_lookup = lookup

    flexnoc_debug_en = logging
    # timebeing we support only one active probe
    ioremap(probe_lookup[probe]['base'])
    return


# always the below function uses two counters
def flexnoc_counterp_setup(probe,
                           counter,
                           trace_port,
                           opcode=0xF,
                           route_id_base=0,
                           route_id_mask=0):
    global probe_lookup

    addr = probe_lookup[probe]['base']
    c0 = addr + probe_lookup[probe]['offsets']['c%d' % (int(counter / 2) * 2)]
    c1 = addr + probe_lookup[probe]['offsets']['c%d' %
                                               (int(counter / 2) * 2 + 1)]
    f = addr + probe_lookup[probe]['offsets']['f%d' % (int(counter / 2))]

    flexnoc_debug_log(
        'B:0x%x, C0:0x%x, C1:0x%x, F:0x%x, %d, 0x%x, 0x%x, 0x%x' %
        (addr, c0, c1, f, trace_port, opcode, route_id_base, route_id_mask))

    # stop ongoing stats if any
    iowrite(addr + 0x008, 0x00000000)  # MAINCTL.StatEn = 0
    iowrite(addr + 0x00C, 0x00000000)  # CFGCTL.GlobalEn = 0

    # setup trace port
    iowrite(addr + 0x010, trace_port)
    iowrite(c0 + 0x00, trace_port)  # COUNTERS_0_PORTSEL
    iowrite(c1 + 0x00, trace_port)  # COUNTERS_1_PORTSEL

    # setup counter sources & triggers
    iowrite(c0 + 0x04,
            0x00000014)  # COUNTERS_0_SRC     (8 - Count BYTES 14 - FiltBytes)
    iowrite(c0 + 0x08, 0x00000002)  # COUNTERS_0_ALARMMODE - OFF
    iowrite(c1 + 0x04, 0x00000010)  # COUNTERS_1_SRC     (Carry from C0)
    iowrite(c1 + 0x08, 0x00000002)  # COUNTERS_1_ALARMMODE - MAX

    # setup filters
    iowrite(f + 0x00, route_id_base)  # Filter 0 Route_id_base
    iowrite(f + 0x04, route_id_mask)  # Filter 0 Route_id_mask
    iowrite(f + 0x08, 0x0)  # Filter 0 Address Base Low
    iowrite(f + 0x0C, 0x0)  # Filter 0 Address Base High
    iowrite(f + 0x10, 0xffffffff)  # Filter 0 window size
    iowrite(f + 0x1C, opcode)  # Filter 0 opcode
    iowrite(f + 0x20, 0x3)  # Filter 0 Status
    iowrite(f + 0x24, 0xF)  # Filter 0 length

    return


# capture the stats for given period and report the 32-bit counter
def flexnoc_counterp_capture(probe, counter=0):
    global probe_lookup

    addr = probe_lookup[probe]['base']
    c0 = addr + probe_lookup[probe]['offsets']['c%d' % (int(counter / 2) * 2)]
    c1 = addr + probe_lookup[probe]['offsets']['c%d' %
                                               (int(counter / 2) * 2 + 1)]

    c0_0 = ioread(c0 + 0x0C)  # COUNTERS_0_VAL
    #time.sleep(1)   # Not Required
    c0_1 = ioread(c0 + 0x0C)  # COUNTERS_0_VAL

    if c0_0 == c0_1:
        flexnoc_debug_log('Counters are frozen. Looks good.')
    else:
        flexnoc_debug_log('c0_0 = %x' % (c0_0))
        flexnoc_debug_log('c0_1 = %x' % (c0_1))
        flexnoc_debug_log(
            'Counters are still running. Calculation could be incorrect.')

    v0 = ioread(c0 + 0x0C)  # COUNTERS_0_VAL
    v1 = ioread(c1 + 0x0C)  # COUNTERS_1_VAL

    return ((v1 << 16) | v0)


def flexnoc_probe_start(probe, statperiod=0x1B):
    global probe_lookup
    addr = probe_lookup[probe]['base']
    flexnoc_debug_log('Setting up probe...')
    iowrite(addr + 0x008, 0x00000008)  # MAINCTL.StatEn = 1
    iowrite(addr + 0x014, 0x00000001)  # FilterLUT = 1

    iowrite(addr + 0x02C, 0x00000000)  # STATALARMMIN
    iowrite(addr + 0x030, 0x00000001)  # STATALARMMAX  - Saturation value
    iowrite(addr + 0x03C, 0x00000001)  # STATALARMEN

    iowrite(
        addr + 0x008, 0x00000098
    )  # MAINCTL .StatEn = 1; .AlarmEn = 1 FiltByteAlwaysChainableEn = 1
    iowrite(addr + 0x024, statperiod)  # STATPERIOD    - 2**duration cycles
    iowrite(addr + 0x014, 0x00000001)  # FilterLUT = 1
    iowrite(addr + 0x00C, 0x00000001)  # CFGCTL.GlobalEn = 1

    flexnoc_debug_log('Monitoring traffic...')
    # this is just arbitrary number, counters will be frozen after STATPERIOD
    #time.sleep(5)  # Not Required
    return
