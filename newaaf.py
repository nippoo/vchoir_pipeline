import aaf2
import sys
import aaf2.components

curr_header_len = 0
curr_file_len = 0

def get_length(currmob):
    global curr_header_len
    global curr_file_len

    if isinstance(currmob, aaf2.components.Filler):
        curr_header_len = currmob.length
    if isinstance(currmob, aaf2.components.SourceClip):
        curr_file_len = currmob.length

    # Does this currmob have children?
    if isinstance(currmob, aaf2.components.OperationGroup):
        for c in currmob.segments:
            get_length(c)
    if hasattr(currmob, 'segment'):
        if hasattr(currmob.segment, 'components'):
            for s in currmob.segment.components:
                get_length(c)


def list_headers_lengths(aaf_file):
    global curr_header_len
    global curr_file_len

    f = aaf2.open(aaf_file)

    lengths = []
    for mob in f.content.mobs:
        if hasattr(mob, 'slots'):
            # We're looking for the long one - let's filter out all the shorter properties
            if(len(mob.slots) > 3):
                for i in range(len(mob.slots)):
                    curr_track_name = mob.slot_at(i).name
                    # get_length(mob.slot_at(i))
                    if hasattr(mob.slot_at(i), 'segment'):
                        # print(type(mob))
                        if hasattr(mob.slot_at(i).segment, 'components'):
                            for s in mob.slot_at(i).segment.components:
                                get_length(s)
                                # print(type(s))
                    if curr_track_name != "Timecode":
                        lengths.append([curr_track_name, curr_header_len, curr_file_len])
                        curr_header_len = 0
                        curr_file_len = 0


    return lengths
