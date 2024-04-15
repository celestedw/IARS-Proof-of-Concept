import hashlib
from typing import Tuple, List

MIN_TIME_WINDOW = 0
MAX_TIME_WINDOW = 180
MAX_BITS = 20

# creates hashes from a sorted list of (frequency, time) tuples. 
# each hash is a hash of a 2 different points: frequency1 + frequency2 + the time difference between the two
# there are ndegree hashes for each (frequency, time) tuple. These 5 are the next ndegree points in the sorted list
def create_hashes(peaks: List[Tuple[int,int]], ndegree, peaksAreSorted = False):
    if not peaksAreSorted:
        peaks.sort(key = lambda x:x[0])
    hashes = []
    for i in range(len(peaks)):
        for j in range(1,ndegree):
            if (i + j) < len(peaks):
                freq1 = peaks[i][0]
                freq2 = peaks[i + j][0]
                t1 = peaks[i][1]
                t2 = peaks[i + j][1]
                t_delta = t2 - t1

                if MIN_TIME_WINDOW <= t_delta <= MAX_TIME_WINDOW:
                    h = hashlib.sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8')) 

                    hashes.append([h.hexdigest()[0:MAX_BITS]])

    return hashes