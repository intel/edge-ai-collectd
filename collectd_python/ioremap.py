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

import os
import mmap


def ioremap(base_addr, size=64 * 1024):
    global mem
    global base

    base = base_addr
    f = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
    mem = mmap.mmap(f,
                    size,
                    mmap.MAP_SHARED,
                    mmap.PROT_READ | mmap.PROT_WRITE,
                    offset=base_addr)

    return


def ioread(addr, len=4):
    global mem
    global base

    mem.seek(addr - base, os.SEEK_SET)
    val = 0
    byte_pos = 0
    while len > 0:
        b = mem.read_byte()
        val |= b << byte_pos  
        #val |= ord(b) << byte_pos
        byte_pos += 8
        len -= 1

    return val


def iowrite(addr, val, len=4):
    global mem
    global base

    mem.seek(addr - base, os.SEEK_SET)
    byte_pos = 0
    while len > 0:
        b = val & (0xFF << byte_pos) >> byte_pos
        mem.write_byte(b)  
        #mem.write_byte(chr(b))
        byte_pos += 8
        len -= 1

    return
