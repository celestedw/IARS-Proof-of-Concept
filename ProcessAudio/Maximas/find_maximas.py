import numpy as np
from matplotlib import pyplot as plt
from matplotlib import image as im
from PIL import Image

# Class stores information about an image and its normalized self. 
class ImageArr:
    name = ''
    im_arr = None
    im_norm = None
    #dimensions
    channels = 3
    height = 0
    width = 0

    def __init__(self, im_arr, name):
        self.im_arr = im_arr
        self.name = name
        self.channels = im_arr.shape[2]
        self.height = im_arr.shape[0]
        self.width = im_arr.shape[1]
        self.norm()
        
    def norm(self):
        self.im_norm = make_image(self.height, self.width, self.channels)
        total = float(0)
        for c in range(self.channels):
            for x in range(self.height):
                for y in range(self.width):
                    total += float(get_pixel(self.im_arr, x, y, c)) / 255.0
        for c in range(self.channels):
            for x in range(self.height):
                for y in range(self.width):
                    self.im_norm[x,y,c] = float(get_pixel(self.im_arr, x, y, c)/255.0)/total

# Makes a black image aka a zeroed array of w rows, h columns, and c channels
def make_image(w, h, c):
    tmp = np.zeros(w * h * c).reshape((w, h, c))
    return tmp

# Returns the value for the pixel at the given channel, or 0 if out of bounds
def get_pixel(im, x, y, c):
    if x < 0 or y < 0 or x >= im.shape[0] or y >= im.shape[1] or c < 0 or c > im.shape[2] or \
        im[x,y,0] == 255 or im[x,y,1] == 255 or im[x,y,2] == 255:
        # out of bounds
        return 0

    return im[x, y, c]

# Changes the pixel to black
def min_pixel(im, x, y):
    if (x >= 0 and y >= 0 and x < im.shape[0] and y < im.shape[1]):
        for c in range(im.shape[2]):
            im[x, y, c] = 0

# Locates the location of the max value within the window
def find_max_in_window(img, h, w, c,window_size):
    m = 0
    max_loc = [h, w]
    for xtmp in range(h - int(window_size/2), h + int(window_size/2)):
        for ytmp in range(w - int(window_size/2), w + int(window_size/2)):
            tmp = get_pixel(img.im_norm, xtmp,ytmp, c)
            if tmp > m:
                m = tmp
                max_loc = [xtmp, ytmp]

    return m, max_loc


# Identifies local maxima within a window. 
# Currently selects a maxima only if it is the max within the window AND the window centered at the maxima
# NOTE: current implementation relies on the viridis colormap. If the colormap of the spectrogram is changed, the
#       algorithm for finding maxima will have to change accordingly 
def identify_max(img,window_size):
    res_list = []
    res_vals = []
    # no need to mess with channels since we're just looking at green (channel 1)
    for x in range(0, img.height, int(window_size/2)):
        for y in range(0, img.width, int(window_size/2)):
            # Get the max within the window and its location
            val,loc = find_max_in_window(img, x, y, 1, window_size)
            m = val
            # Check if that val/loc is the max within its own window       
            for ytmp in range(loc[1] - int(window_size/2), loc[1] + int(window_size/2)):
                for xtmp in range(loc[0] - int(window_size/2), loc[0]+ int(window_size/2)):
                    tmp = get_pixel(img.im_norm, xtmp,ytmp, 1)
                    if tmp > m:
                        m = tmp
            if val == m:
                res_list.append((tuple([loc[0],loc[1]])))
                res_vals.append(val)
    
    return res_list, sum(res_vals)/len(res_vals)

# Keep maxima stronger or equal to the average value
def prune_max(img, max_list, avg):
    pruned_list = []
    res_img = np.copy(img.im_arr)
    for [x, y] in max_list:
        if img.im_norm[x, y, 1]  == max(img.im_norm[x,y,1], avg):
            pruned_list.append(tuple([x,y]))
            for i in range(5):
                min_pixel(res_img, x-i, y-i)
                min_pixel(res_img, x-i, y+i)
                min_pixel(res_img, x+i, y-i)
                min_pixel(res_img, x+i, y+i)

    return pruned_list, res_img

# Finds peaks within an image
# NOTE: curently only support 3channel images: so JPG's. PNG's...not so much.
def find_identifiers(im, window_size):
    print("entering find_maxes with a window of size of ", window_size)
    
    res_list, avg = identify_max(im, window_size)
    # prune results to only keep the darkest points -- an attempt to limit noise
    pruned_list, res_img = prune_max(im, res_list, avg)
    
    # right now identified points are being marked with a black x
    img = Image.fromarray(np.array(res_img).astype(np.uint8), "RGB")
    img.save("ProcessAudio/Results/Maxima/" + im.name + "_maxima" + str(window_size) + ".jpg")

    return pruned_list
