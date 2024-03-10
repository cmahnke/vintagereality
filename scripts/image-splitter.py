#!/usr/bin/env python

from PIL import Image, ImageDraw
import argparse, pathlib, json, sys, math
from packaging import version
from termcolor import cprint

# Duration for Wigglegrams im ms
defaultDuration = 100

# How many iterations for autoalignment, 20 is mostly sufficient, 50 improve results
auto_align_iterations = 75

# See http://www.sview.ru/en/help/input/
# See https://note.nkmk.me/en/python-pillow-concat-images/
def crossed_eyed(left, right, file, format='jpeg'):
    ce = Image.new('RGB', (right.width + left.width, right.height))
    ce.paste(right, (0, 0))
    ce.paste(left, (right.width, 0))
    ce.save(file, format)
    return ce

def depth_map(pilLeft, pilRight, file):
    # See https://github.com/pairote/stereo2depth
    # See https://docs.opencv.org/4.9.0/d3/d14/tutorial_ximgproc_disparity_filtering.html
    # Parameters from all steps are defined here to make it easier to adjust values.
    resolution      = 1.0    # (0, 1.0]
    numDisparities  = 16     # has to be dividable by 16
    blockSize       = 5      # (0, 25]
    windowSize      = 5      # Usually set equals to the block size
    uniquenessRatio = 15
    filterCap       = 63     # [0, 100]
    lmbda           = 80000  # [80000, 100000]
    sigma           = 1.2
    brightness      = 0      # [-1.0, 1.0]
    contrast        = .7      # [0.0, 3.0]

    gLeft = cv.cvtColor(np.array(pilLeft), cv.COLOR_RGB2GRAY)
    gRight = cv.cvtColor(np.array(pilRight), cv.COLOR_RGB2GRAY)

    if is_print(gLeft, gRight):
        cprint("Detected printed image with raster, smoothen", 'yellow')
        #TODO: This doens't really help
        left = cv.medianBlur(gLeft, 5)
        right = cv.medianBlur(gRight, 5)
    else:
        cprint("Image is almost certainly not a printed image", 'green')
        left = gLeft
        right = gRight

    height, width = left.shape[:2]

    left_matcher = cv.StereoSGBM_create(
        minDisparity = 0,
        numDisparities = numDisparities,
        blockSize = blockSize,
        P1 = 8 * 3 * windowSize ** 2,
        P2 = 32 * 3 * windowSize ** 2,
        disp12MaxDiff = 1,
        uniquenessRatio = uniquenessRatio,
        speckleWindowSize = 0,
        speckleRange = 2,
        preFilterCap = filterCap,
        mode = cv.STEREO_SGBM_MODE_HH
        #mode = cv.STEREO_SGBM_MODE_SGBM_3WAY
    )

    right_matcher = cv.ximgproc.createRightMatcher(left_matcher)

    # Step 5 - Setup a disparity filter to deal with stereo-matching errors.
    #          It will detect inaccurate disparity values and invalidate them, therefore making the disparity map semi-sparse.
    wls_filter = cv.ximgproc.createDisparityWLSFilter(matcher_left = left_matcher)
    wls_filter.setLambda(lmbda)
    wls_filter.setSigmaColor(sigma)

    # Step 6 - Perform stereo matching to compute disparity maps for both left and right views.
    displ = left_matcher.compute(left, right)
    dispr = right_matcher.compute(right, left)

    # Step 7 - Perform post-filtering
    leftB = cv.copyMakeBorder(left, top = 0, bottom = 0, left = np.uint16(numDisparities / resolution), right = 0, borderType= cv.BORDER_CONSTANT, value = [155,155,155])
    filteredImg = wls_filter.filter(displ, leftB, None, dispr)

    # Step 8 - Adjust image resolution, brightness, contrast, and perform disparity truncation hack
    filteredImg = filteredImg * resolution
    filteredImg = filteredImg + (brightness / 100.0)
    filteredImg = (filteredImg - 128) * contrast + 128
    filteredImg = np.clip(filteredImg, 0, 255)
    filteredImg = np.uint8(filteredImg)
    filteredImg = filteredImg[0:height, np.uint16(numDisparities / resolution):width]
    outImg = cv.medianBlur(filteredImg, 5)

    if isinstance(file, pathlib.PurePath):
        file = str(file)

    cv.imwrite(file, outImg, [cv.IMWRITE_JPEG_QUALITY, 100])

def cut_stereo(coords, im):
    left_left = coords['left']['position']['x']
    left_top = coords['left']['position']['y']
    left_right = coords['left']['size']['x'] + coords['left']['position']['x']
    left_bottom = coords['left']['size']['y'] + coords['left']['position']['y']

    right_left = coords['right']['position']['x']
    right_top = coords['left']['position']['y']
    right_right = coords['right']['size']['x'] + coords['right']['position']['x']
    right_bottom =  coords['right']['size']['y'] + coords['right']['position']['y']

    if (coords['left']['size']['x'] != coords['right']['size']['x']):
        cprint('Width (x) doesn\'t match!', 'yellow', end=' ')
        if (coords['left']['size']['x'] < coords['right']['size']['x']):
            cprint ("Left image is narrower", 'yellow')
            cprint("Old left for right image {}, right for right image {} - width {}".format(right_left, right_right, coords['right']['size']['x']), 'yellow')
            right_left = (coords['right']['position']['x'] + (coords['right']['size']['x'] - coords['left']['size']['x']) / 2)
            right_right = coords['left']['size']['x'] + right_left
            print("New left for right image {}, right for right image {} - width {}".format(right_left, right_right, right_right - right_left))
        else:
            cprint ('Right image is narrower', 'yellow')
            cprint("Old left for left image {}, right for left image {} - width {}".format(left_left, left_right, coords['left']['size']['x']), 'yellow')
            left_left = coords['left']['position']['x'] + ((coords['left']['size']['x'] - coords['right']['size']['x']) / 2)
            left_right = coords['right']['size']['x'] + left_left # change
            cprint("New left for left image {}, right for left image {} - width {}".format(left_left, left_right, left_right - left_left), 'yellow')

    if ( coords['left']['size']['y'] != coords['right']['size']['y']):
        cprint("Height (y) doesn't match!", 'yellow', end=" ")

        if (coords['left']['size']['y'] < coords['right']['size']['y']):
            cprint ('Left image is smaller', 'yellow')
            cprint("Old top for right image {}, bottom for right image {}".format(right_top, right_bottom), 'yellow')
            right_top = (coords['right']['position']['y'] + (coords['right']['size']['y'] - coords['left']['size']['y']) / 2)
            right_bottom = coords['left']['size']['y'] + right_top
            cprint("New top for right image {}, bottom for right image {}".format(right_top, right_bottom), 'yellow')
        else:
            cprint ('Right image is smaller', 'yellow')
            cprint("Old top for left image {}, bottom for left image {}".format(left_top, left_bottom), 'yellow')
            left_top = (coords['left']['position']['y'] + (coords['left']['size']['y'] - coords['right']['size']['y']) / 2)
            left_bottom = coords['right']['size']['y'] + left_top
            cprint("New top for left image {}, bottom for left image {}".format(left_top, left_bottom), 'yellow')

    left = im.crop((left_left, left_top, left_right, left_bottom))
    right = im.crop((right_left, right_top, right_right, right_bottom))
    return (left, right)

# See https://parth3d.co.uk/splitting-anaglyph-images-in-python
def cut_anaglyph(coords, im):
    if not coords['left'] or not coords['right']:
        h, w = im.size
        for side in ['left', 'right']:
            coords[side]['position']['x'] = 0
            coords[side]['position']['y'] = 0
            coords[side]['size']['x'] = w
            coords[side]['size']['y'] = h

    if not coords['left'] == coords['right']:
        cprint('Both images should have the same size!', 'red')
    if im.mode == "RGBA":
        im = im.convert('RGB')

    left_left = coords['left']['position']['x']
    left_top = coords['left']['position']['y']
    left_right = coords['left']['size']['x'] + coords['left']['position']['x']
    left_bottom = coords['left']['size']['y'] + coords['left']['position']['y']
    im = im.crop((left_left, left_top, left_right, left_bottom))

    left = Image.new("RGB", (coords['left']['size']['x'], coords['left']['size']['y']), (255,255,255))
    right = Image.new("RGB", (coords['right']['size']['x'], coords['right']['size']['y']), (255,255,255))
    second_color = ''
    if 'second_color' in coords:
        second_color = coords['second_color']
    for y in range(0, coords['left']['size']['y']):
        for x in range(0, coords['left']['size']['x']):
            col = im.getpixel((x, y))
            lc = int(col[0])
            left.putpixel((x,y), (lc, lc, lc))
            if second_color == "green":
                rc = int(col[1])
            elif second_color == "blue":
                rc = int(col[2])
            else:
                rc = int((col[1] + col[2]) / 2)
            right.putpixel((x,y), (rc, rc, rc))

    return (left, right)

def get_patch (im):
    h, w = im.size
    (nw, nx) = (w / 3, w / 3)
    (nh, ny) = (h / 30, h / 30)
    return im.crop((nx, ny, nx + nw, ny + nh))

def is_print(left, right):
    edges = cv.Canny(left, 50, 150, apertureSize=5)
    height, width = left.shape[:2]
    minLength = math.sqrt(math.pow(height / 3, 2) + math.pow(width / 3, 2))
    threshold = width / 3
    lines = cv.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=minLength, maxLineGap=10)
    numLines = 0
    if lines is not None:
        numLines = len(lines)
    cprint(f"Checking for print: Image height: {height}, width: {width}, min length of lines {minLength}, lines threshold: {threshold}, lines found: {numLines}", 'yellow')

    if lines is not None and len(lines) > threshold:
        return True
    return False

def debug_processor(im, file):
    if file is not None:
        if isinstance(im, tuple):
            path = pathlib.Path(file)
            im[0].save(path.parent.joinpath(path.stem + 'L' + path.suffix))
            im[1].save(path.parent.joinpath(path.stem + 'R' + path.suffix))
        else:
            im.save(file)

# See https://mattmaulion.medium.com/white-balancing-an-enhancement-technique-in-image-processing-8dd773c69f6
def white_balance(im, coords = None, file = None, opts = None):
    import numpy
    mode = "mean"
    def single(im, opts):
        if im.mode == "RGBA":
            im = im.convert('RGB')
        image = numpy.asarray(im)
        image_patch = numpy.asarray(get_patch(im))
        if mode == 'mean':
            image_gt = ((image * (image_patch.mean() / image.mean(axis=(0, 1)))).clip(0, 255).astype(int))
        elif mode == 'max':
            image_gt = ((image * 1.0 / image_patch.max(axis=(0,1))).clip(0, 1))
        else:
            cprint("Mode not set! Failing!", 'red')

        return Image.fromarray(image_gt.astype('uint8'))

    if isinstance(im, tuple):
        retIm = (single(im[0], opts), single(im[1]. opts))
    else:
        retIm = single(im, opts)

    debug_processor(im, file)
    return retIm

def blank_out(im, coords = None, file = None, opts = None):
    color = "white"
    def single(im, opts):
        draw = ImageDraw.Draw(im)
        if opts is not None and len(opts) == 4:
            draw.rectangle(((opts[0], opts[1]), (opts[0] + opts[2], opts[1] + opts[3])), fill=color, width=0)
        return im

    if isinstance(im, tuple):
        retIm = (single(im[0], opts), single(im[1]. opts))
    else:
        retIm = single(im, opts)

    debug_processor(retIm, file)
    return retIm

def normalize(im, coords = None, file = None, opts = None):
    import numpy as np
    import cv2 as cv
    def single(im):
        cvAr = cv.cvtColor(np.array(im), cv.COLOR_RGB2GRAY)
        normalized = cv.normalize(cvAr, None, beta=0, alpha=255, norm_type=cv.NORM_MINMAX)
        return Image.fromarray(cv.cvtColor(normalized, cv.COLOR_GRAY2RGB))

    if isinstance(im, tuple):
        retIm = (single(im[0]), single(im[1]))
    else:
        retIm = single(im)

    debug_processor(retIm, file)
    return retIm

# TODO: This is just a placeholder for auto alignment metadata
def auto_align(im, coords = None, file = None, opts = None):
    return im

def get_processors(config, phase = 'preprocess'):
    if isinstance(coords[phase], list):
        methods = coords[phase]
    else:
        methods = [coords[phase]]
    processors = []
    for method in methods:
        if isinstance(method, dict):
            params = method['args']
            method = method['method']
        else:
            params = {}
        processors.append({'method': method, 'params': params})
    return processors

parser = argparse.ArgumentParser(description='Extract steroscopic images')
parser.add_argument('--image', type=pathlib.Path, help='Image to process', required=True)
parser.add_argument('--coords', type=pathlib.Path, help='File containing coordinates', required=True)
parser.add_argument('--output', choices=['gif', 'jps', 'images', 'jpg', 'mpo', 'depthmap'], action='append', nargs='+', help='Output format', default=[])
parser.add_argument('--samesize', '-s', help='Force same size (implies advanced)', default=False, action='store_true')
parser.add_argument('--advanced', '-a', help='Use advanced features provided by StereoscoPy', default=False, action='store_true')
parser.add_argument('--debug', '-d', help='Print information about JXL bindings', default=False, action='store_true')

args = parser.parse_args()

images_suffix = args.image.suffix

if args.debug:
    import jxlpy
    print("jxlpy: {}, libjxl: {}, pillow: {}".format(jxlpy.__version__, jxlpy._jxl_version, Image.__version__))

if str(args.image).endswith('.jxl'):
    from jxlpy import JXLImagePlugin
    images_suffix = '.jpg'

im = Image.open(args.image)

coords = json.load(args.coords.open())

if (len(args.output) == 0):
    outputs = ['images']
else:
    outputs = sum(args.output, [])

cprint('Requested output formats: ' + ', '.join(outputs), 'yellow')
same_size = False
advanced = False

if args.samesize:
    same_size = True
    cprint('Forcing same image size', 'yellow')
    advanced = True

if ('jpg' in outputs):
    cprint('Anayglyph output requires -s and -a, setting it automatically', 'yellow')
    advanced = True
    same_size = True

if ('depthmap' in outputs):
    cprint('Depth map output requires -s and -a, setting it automatically', 'yellow')
    advanced = True
    same_size = True

if args.advanced and not advanced:
    advanced = True
    cprint('Using advanced features provided by StereoscoPy and OpenCV', 'yellow')

if advanced:
    import stereoscopy
    import numpy as np
    import cv2 as cv

leftFileName = args.image.parent.joinpath(args.image.stem + '-left' + images_suffix)
rightFileName = args.image.parent.joinpath(args.image.stem + '-right' + images_suffix)
if coords['left'] and coords['right']:
    cprint("Left start position {},{}, size {}, {} - File name {}".format(coords['left']['position']['x'], coords['left']['position']['y'], coords['left']['size']['x'], coords['left']['size']['y'], leftFileName), 'yellow')
    cprint("Right start position {},{}, size {}, {} - File name {}".format(coords['right']['position']['x'], coords['right']['position']['y'], coords['right']['size']['x'], coords['right']['size']['y'], rightFileName), 'yellow')

if 'preprocess' in coords and advanced:
    for processor in get_processors(coords, 'preprocess'):
        preprocessFileName = args.image.parent.joinpath(args.image.stem + '-pre-' + processor['method'] + images_suffix)
        im = locals()[processor['method']](im, coords, preprocessFileName, processor['params'])

if not 'type' in coords:
    (left, right) = cut_stereo(coords, im)
    if same_size:
        (left, right) = stereoscopy.auto_align((left, right), shrink=same_size, iterations=auto_align_iterations)
elif 'type' in coords and coords['type'] == 'anaglyph':
    (left, right) = cut_anaglyph(coords, im)

if 'postprocess' in coords and advanced:
    for processor in get_processors(coords, 'postprocess'):
        postprocessFileName = args.image.parent.joinpath(args.image.stem + '-post-' + processor['method'] + images_suffix)
        (left, right) = locals()[processor['method']]((left, right), coords, postprocessFileName, processor['params'])

# See https://blog.miguelgrinberg.com/post/take-3d-pictures-with-your-canon-dslr-and-magic-lantern

if ('gif' in outputs):
    gifFileName = args.image.parent.joinpath(args.image.stem + '.gif')
    left.save(gifFileName, save_all=True, append_images=[right], duration=(defaultDuration / 1000) * 100, loop=0, dispose=2)
if ('jps' in outputs):
    ceFileName = args.image.parent.joinpath(args.image.stem + '.jps')
    crossed_eyed(left, right, ceFileName)
if ('jpg' in outputs):
    anagFileName = args.image.parent.joinpath(args.image.stem + '-anaglyph.jpg')
    stereoscopy.create_anaglyph((left, right), method="gray").save(anagFileName)
if ('depthmap' in outputs):
    ceFileName = args.image.parent.joinpath(args.image.stem + '-depthmap.jpg')
    depth_map(left, right, ceFileName)
if ('images' in outputs):
    left.save(leftFileName)
    right.save(rightFileName)
if ('mpo' in outputs):
    if version.parse(Image.__version__) < version.parse('9.3.0'):
        cprint('Your version of the Pillow (PIL) library is to old ({}), it only has partial MPO support. At least version 9.3.0 is required. MPO output is disabled'.format(Image.__version__),  'red')
    else:
        if version.parse(Image.__version__) < version.parse('9.4.0'):
            cprint('Pillow version 9.4.0 contains several improvements for MPO, consider updating.', 'yellow')
        mpoFileName = args.image.parent.joinpath(args.image.stem + '.mpo')
        left.save(mpoFileName, save_all=True, append_images=[right])
