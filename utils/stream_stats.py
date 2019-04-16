from models.streams import Stream

def GetDataSetStat(streams: [Stream]) :
    avg_length = 0
    avg_number = 0
    tmin = streams[0].m_intervals[0].m_start
    tmax = streams[0].m_intervals[-1].m_end
    for stream in streams:
        avg_length = avg_length + stream.m_length
        avg_number = avg_number + stream.m_size
        if stream.m_intervals[0].m_start < tmin : 
            tmin = stream.m_intervals[0].m_start
        if stream.m_intervals[-1].m_end > tmax :
            tmax = stream.m_intervals[-1].m_end
        
    duration = tmax - tmin
    avg_length = avg_length / len(streams)
    avg_number = avg_number / len(streams)
    avg_density = avg_length / duration
    return [duration, avg_length, avg_density, avg_number]

def GetStreamStat(stream : Stream) :
    tmin = stream.m_intervals[0].m_start
    tmax = stream.m_intervals[-1].m_end
    return [tmax -tmin, stream.m_length, stream.m_length/(tmax-tmin), len(stream.m_intervals)]