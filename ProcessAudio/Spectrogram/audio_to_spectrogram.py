import matplotlib.pyplot as plt
import matplotlib.image as im
import scipy.io.wavfile as wavfile
import noisereduce as nr
import math

# Generates and returns spectrogram images in a list along with a list of their extents (dimensions used to convert pixels to (frequency,time) pairs)
# If use_intervals is true, then audio will be split into intervals (of size interval_time) then processed. 
# Labeled spectrograms will be generated for each interval
# interval_time is in seconds. use_intervals is recommended for files larger than interval_time
# NOTE: Currently. the audio file must be a wav file. 
def audio_to_spectrogram(file, noise_reduction, interval_time, use_intervals):

    images = []; extents = []; times = [] 

    #load data, rate is sample rate, data is audio data
    rate, data = wavfile.read(file)

    # perform noise reduction, prop_decrease controls how much % noise reduction, 1.0 is 100%
    reduced_noise = nr.reduce_noise(y=data, sr=rate, prop_decrease = noise_reduction)

    #create reduced noise .wav file
    filename = file[file.index('/')+1:file.index('.')] + str(noise_reduction)
    new_file_name = f'ProcessAudio/Results/noiseReduce_{filename}_{str(rate)}.wav'
    wavfile.write(new_file_name, rate, reduced_noise)

    #read reduced noise .wav file, Fs is sample rate, aud is data
    sampling_frequency, aud = wavfile.read(new_file_name)

    #calculate audio length
    n = aud.size
    time = n / sampling_frequency

    if use_intervals == False:
        print(f"time: {str(time)}"); print(f"sampling frequency: {str(sampling_frequency)}")

        #plot specgram
        power_Spectrum, frequencies_Found, timeSpec, imageAxis = plt.specgram(aud, Fs=sampling_frequency, mode = 'phase')

        plt.ylim(0,sampling_frequency/2.0)
        plt.xlim(0,n/sampling_frequency)
        plt.xlabel(f'time {int(n / sampling_frequency / 60)} minutes')
        plt.ylabel('frequency kHz')
        plt.title(f'{file} spectrogram {str(noise_reduction)} noise reduction')

        plt.savefig(f'ProcessAudio/Results/Spectrograms/spectrogram_fig_{filename}.jpg')

        #get just image, no axis
        plt.title(''); plt.axis('off')
        plt.savefig(
            f"ProcessAudio/Results/Spectrograms/spectrogram_{filename}.jpg",
            bbox_inches='tight',
            pad_inches=0,
        )
        f = im.imread(f"ProcessAudio/Results/Spectrograms/spectrogram_{filename}.jpg")
        plt.close()

        return [f], [time], [imageAxis.get_extent()]
    else:
        if interval_time <= 0:
            print("enter a valid interval time")
            return 0,0
        num_intervals = int(time/interval_time)

        #if the last interval isn't too small, then we add 1 to num_intervals to not miss anything
        if (time % interval_time > 5):
            num_intervals += 1
        num_intervals = max(num_intervals, 1)
        print("num intervals: ", num_intervals)
        starting_point = 0; ending_point = interval_time; current_interval_time = interval_time

        for i in range(int(num_intervals)):
            #if ending point is greater than time, subtract back down to time
            if (ending_point > int(time)):
                ending_point = ending_point - (ending_point-math.ceil(time))
                plt.xlabel(f'time {str((ending_point - starting_point) / 60.0)} minutes')
            else:
                plt.xlabel(f'time {str(int(n / sampling_frequency / 60) / num_intervals)} minutes')
            #set end audio value after setting ending_point
            end = sampling_frequency*ending_point
            #if on the last interval, set current_interval_time to how much time left there is, then filter audio to specific time interval
            if (i == (int(num_intervals) - 1)):
                current_interval_time = time - (num_intervals-1)*interval_time
                interval_audio = aud[starting_point*sampling_frequency:]
            else:
                 #otherwise just set current_interval_time to interval_time
                 current_interval_time = interval_time
                 interval_audio = aud[starting_point*sampling_frequency:end]

            print(f'starting_point: {str(starting_point)}'); print(f"ending_point : {str(ending_point)}")
            print(f"time: {str(time)}"); print(f"time of selected interval: {str(current_interval_time)}")
            print(f"sampling frequency: {str(sampling_frequency)}"); print(f'interval: {str(i + 1)}')
            
            #set y axis and title
            plt.ylim(0,sampling_frequency/2.0); plt.xlim(0,n/sampling_frequency)
            plt.ylabel('frequency kHz')
            plt.title(
                f'{file} interval {str(i + 1)} spectrogram ({str(starting_point)} to {str(ending_point)}'
                + ') seconds \n'
                + str(noise_reduction)
                + ' noise reduction'
            )
            #plot spectrogram and save file
            powerSpectrum, frequenciesFound, timeSpec, imageAxis = plt.specgram(interval_audio, Fs=sampling_frequency, mode='phase')
            plt.savefig(f'ProcessAudio/Results/Spectrograms/spectrogram_fig_{filename}interval{str(i + 1)}.jpg')
            #get just image, no axis
            plt.title(''); plt.axis('off')
            plt.savefig(
                f"ProcessAudio/Results/Spectrograms/spectrogram_{filename}interval{str(i + 1)}.jpg",
                bbox_inches='tight',
                pad_inches=0,
            )
            f = im.imread(f"ProcessAudio/Results/Spectrograms/spectrogram_{filename}interval{str(i + 1)}.jpg")
            plt.close()

            # append to images, times and extents array
            images.append(f); times.append(current_interval_time); extents.append(imageAxis.get_extent())
            # change starting and ending points
            starting_point = starting_point + interval_time; ending_point = ending_point + interval_time
            
    return images, times, extents