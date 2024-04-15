import ProcessAudio.Spectrogram.audio_to_spectrogram as a2s
import ProcessAudio.Maximas.find_maximas as fm
import ProcessAudio.Hash.lsh as lsh
import ProcessAudio.Hash.match as m
import json
import os
import shutil


freq_time_arr = []

def process_audio(file, window_max = 40.75, window_min = 15, interval = 60, use_interval = True): 
    print("Processing audio file "  +file)
    pics,ts, extents = a2s.audio_to_spectrogram(file, noise_reduction=0.99, interval_time = interval, use_intervals = use_interval)
    freq_time_arr = []
    name = file[file.rindex('/')+1:file.rindex('.')]


    for i in range(len(pics)):
        #NOTE: in images, x corresponds to row and y corresponds to column. This means that x increases vertically and y increases horizontally
        #NOTE: However, the extent is in the form (ystart, yend, xstart, xend) where y values 
        #      correspond to width and x values correspond to height
        ytics = (extents[i][1] - extents[i][0]) / pics[0].shape[1]
        ystart = extents[i][0]
        xtics = (extents[i][3] - extents[i][2]) / pics[0].shape[0]
        xstart = extents[i][3] # the 0 index is at the top of the image, so we have to subtract from highest frequency
        #print('xtics: ', xtics, ', ytics: ', ytics, ', xstart: ', xstart, ', ystart: ', ystart)

        window_size = max(int((window_max - 0.15*(ts[i]-ystart))), window_min)

        # get maxima
        arr_max = fm.find_identifiers(fm.ImageArr(pics[i], name + '_interval_' + str(i+1)),window_size)

        # convert [x,y] of image (in pixels) to [frequency, time] of spectrogram
        for pixel in arr_max:
            freq_time_arr.append(tuple([xstart - xtics * pixel[0], i*interval + (ystart + ytics * pixel[1])]))
    print(str(len(freq_time_arr)) + ' peaks found')

    # get hashes
    hashes = lsh.create_hashes(freq_time_arr,ndegree=5,peaksAreSorted=False)
    
    # match against db
    incident_num, dict_to_update = m.match(hashes, read_json())
    # add the audio hash to the db
    update(incident_num, dict_to_update, hashes)

    # copy audio file to an incident folder
    directory = 'Incidents/incident_' + str(incident_num)
    if not os.path.exists(directory):
        # no match. Create a new folder for the new incident
        os.makedirs(directory)
    print("copying file to ", 'Incidents/incident_' + str(incident_num))
    # save audio to the incident's folder
    shutil.copyfile(file, directory + '/' + name + '.wav') 

 
def update(incident_num, dict, hashes):
    # format of a JSON file: 
    '''
    data = {
        "incidentName": incident_num,
        "fingerprints": [[hashes],...]
    }
    '''
    if dict is None:
        # no match. Create new
        dict = {
            "incidentName": incident_num, 
            "fingerprints": [hashes]
            }
    else:
        # match. Add on to the JSON file
        dict["fingerprints"].append(hashes)

    # Update the JSON file 
    with open('JSON/incident_' + str(incident_num)+ '.json', 'w') as outfile:
        outfile.write(json.dumps(dict, indent=4))

def read_json():
    dirs = []
    if (os.path.exists('JSON')): 
        for file in os.listdir('JSON'):
            if file.endswith(".json"):
                with open('JSON/' + file, 'r') as openfile:
                    dirs.append(json.load(openfile))
    return dirs