# automatically generated by the FlatBuffers compiler, do not modify

# namespace: 

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class TS_STATUS_UPDATE(object):
    __slots__ = ['_tab']

    @classmethod
    def SizeOf(cls):
        return 1

    # TS_STATUS_UPDATE
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # TS_STATUS_UPDATE
    def TsStatus(self): return self._tab.Get(flatbuffers.number_types.Int8Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))

def CreateTS_STATUS_UPDATE(builder, tsStatus):
    builder.Prep(1, 1)
    builder.PrependInt8(tsStatus)
    return builder.Offset()
