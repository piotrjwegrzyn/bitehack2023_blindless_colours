import colour
from PIL import Image
import numpy as np
import base64
from io import BytesIO

'''
Attributes
----------
imageBase64 : str
    Image decoded from base64
'''
def readImage(imageBase64):
    return Image.open(BytesIO(base64.b64decode(str.encode(imageBase64))))

'''
Attributes
----------
image : PIL.Image
    Sniping image to 5 parts and getting their dominant colour
'''
def imageToParts(image):
    w, h = image.size
    
    parts = [.2, .1, .4, .1, .2]
    dominant_colors = list()
    last_width = 0
    for part_percent in parts:
        pixels = w * part_percent
        cropped_image = image.crop((last_width, 0, last_width + pixels, h))
        last_width += pixels
        dominant_colors.append(getDominantColor(cropped_image))
    return dominant_colors

'''
Attributes
----------
image : PIL.Image
    Return dominant color in given image
'''
def getDominantColor(image):
    width, height = image.size
    image = image.resize((width, height),resample = 0)
    pixels = image.getcolors(width * height)
    sorted_pixels = sorted(pixels, key=lambda t: t[0])
    dominant_color = sorted_pixels[-1][1]
    return dominant_color

'''
Attributes
----------
r : int in range 0-255
g : int in range 0-255
b : int in range 0-255
    Converting RGB values to wavelength and dominant wavelength
'''
def RGBToWaveLength(r,g,b):
    RGB_f = np.array([r,g,b]) / 255

    RGB_l = colour.models.eotf_sRGB(RGB_f)
    XYZ = colour.RGB_to_XYZ(
        RGB_l,
        colour.models.RGB_COLOURSPACE_sRGB.whitepoint,
        colour.models.RGB_COLOURSPACE_sRGB.whitepoint,
        colour.models.RGB_COLOURSPACE_sRGB.matrix_RGB_to_XYZ,
    )

    xy = colour.XYZ_to_xy(XYZ)
    
    wl, xy_1, xy_2 = colour.dominant_wavelength(
        xy, colour.models.RGB_COLOURSPACE_sRGB.whitepoint
    )

    wl, xy_1, xy_2 = colour.convert(RGB_f, "Output-Referred RGB", "Dominant Wavelength")

    return wl.tolist(), xy_1.tolist(), xy_2.tolist()


'''
Attributes
----------
wave_lengths : float
    Convert wavelength to frequency
'''
def wavelengthToFreq(wave_lengths):
    frequencies = list()
    for wl in wave_lengths:
        frequencies.append(299792458 // wl[0]*10e9)
    return frequencies  # This is returned in HZ

'''
Attributes
----------
imageBase64 : PIL.Image
    Return dominant color in given image
'''
def getConvertedData(imageBase64):
    image = readImage(imageBase64)

    dominant_colors = imageToParts(image)
    wave_lengths = [RGBToWaveLength(r,g,b) for r,g,b in dominant_colors]
    frequencies = wavelengthToFreq(wave_lengths)

    return {"dominant_colors": dominant_colors, "wave_lengths": wave_lengths, "frequencies": frequencies}
