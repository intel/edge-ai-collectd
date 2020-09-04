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
from flexnoc import *

kmb_probe_lookup = {
    "dss": {
        "base": 0x3B400000,
        "offsets": {
            "f0": 0x44,
            "f1": 0x80,
            "f2": 0xBC,
            "f3": 0xF8,
            "c0": 0x134,
            "c1": 0x148,
            "c2": 0x15C,
            "c3": 0x170,
        },
    }
}


# default test routine to track port 4
def _main():

    duration = 0x1B  # 268 ms@500MHz or 191 ms@700MHz
    clk = 700000  # 700MHz as per Keembay_VPU_Databook 1.11
    s = 2**duration / (clk * 1000.0)  # convert clk,duration to seconds

    flexnoc_probe_init(probe="dss", lookup=kmb_probe_lookup)
    flexnoc_counterp_setup(probe="dss", counter=0, trace_port=4)
    flexnoc_counterp_setup(probe="dss", counter=2, trace_port=4)
    flexnoc_probe_start(probe="dss")
    # 5 sec sleep
    #time.sleep(2)
    kb0 = flexnoc_counterp_capture(probe="dss", counter=0) / 1024.0  # sleep(1)
    kb2 = flexnoc_counterp_capture(probe="dss", counter=2) / 1024.0  # sleep(1)

    print("Traffic in C0 = %8.2f kbps" % (kb0 / s))
    print("Traffic in C2 = %8.2f kbps" % (kb2 / s))

    #return (kb0 / s), (kb2 / s)
    return


if __name__ == "__main__":
    _main()
