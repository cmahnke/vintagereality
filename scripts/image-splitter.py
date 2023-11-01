#!/usr/bin/env python

from PIL import Image
import argparse, pathlib, json, sys
from packaging import version
from termcolor import cprint

# Duration for Wigglegrams im ms
defaultDuration = 100

# See http://www.sview.ru/en/help/input/
# See https://note.nkmk.me/en/python-pillow-concat-images/
def crossed_eyed(left, right, file, format='jpeg'):
    ce = Image.new('RGB', (right.width + left.width, right.height))
    ce.paste(right, (0, 0))
    ce.paste(left, (right.width, 0))
    ce.save(file, format)
    return ce

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
    #from matplotlib import pyplot as plt
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

# See https://mattmaulion.medium.com/white-balancing-an-enhancement-technique-in-image-processing-8dd773c69f6
def white_balance(im, coords = None, file = None):
    import numpy
    mode = 'mean'
    if im.mode == "RGBA":
        im = im.convert('RGB')
    image = numpy.asarray(im)
    image_patch = numpy.asarray(get_patch(im))
    if mode == 'mean':
       image_gt = ((image * (image_patch.mean() / image.mean(axis=(0, 1)))).clip(0, 255).astype(int))
    if mode == 'max':
       image_gt = ((image * 1.0 / image_patch.max(axis=(0,1))).clip(0, 1))
    im = Image.fromarray(image_gt.astype('uint8'))
    if file != None:
        im.save(file)
    return im

parser = argparse.ArgumentParser(description='Extract steroscopic images')
parser.add_argument('--image', type=pathlib.Path, help='Image to process', required=True)
parser.add_argument('--coords', type=pathlib.Path, help='File containing coordinates', required=True)
parser.add_argument('--output', choices=['gif', 'jps', 'images', 'jpg', 'mpo'], action='append', nargs='+', help='Output format', default=[])
parser.add_argument('--samesize', '-s', help='Force same size (implies advanced)', default=False, action='store_true')
parser.add_argument('--advanced', '-a', help='Use advanced features provided by StereoscoPy', default=False, action='store_true')

args = parser.parse_args()

images_suffix = args.image.suffix

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
    cprint('Anayglyph output requires -s and -a, setting it automaticlly', 'yellow')
    advanced = True
    same_size = True

if args.advanced and not advanced:
    advanced = True
    cprint('Using advanced features provided by StereoscoPy', 'yellow')

if advanced:
    import stereoscopy

leftFileName = args.image.parent.joinpath(args.image.stem + '-left' + images_suffix)
rightFileName = args.image.parent.joinpath(args.image.stem + '-right' + images_suffix)
if coords['left'] and coords['right']:
    cprint("Left start position {},{}, size {}, {} - File name {}".format(coords['left']['position']['x'], coords['left']['position']['y'], coords['left']['size']['x'], coords['left']['size']['y'], leftFileName), 'yellow')
    cprint("Right start position {},{}, size {}, {} - File name {}".format(coords['right']['position']['x'], coords['right']['position']['y'], coords['right']['size']['x'], coords['right']['size']['y'], rightFileName), 'yellow')

if 'preprocess' in coords and advanced:
    if isinstance(coords['preprocess'], list):
        methods = coords['preprocess']
    else:
        methods = [coords['preprocess']]
    for method in methods:
        preprocessFileName = args.image.parent.joinpath(args.image.stem + '-' + method + images_suffix)
        locals()[method](im, coords, preprocessFileName)

if not 'type' in coords:
    (left, right) = cut_stereo(coords, im)
    if same_size:
        (left, right) = stereoscopy.auto_align((left, right), shrink=same_size)
elif 'type' in coords and coords['type'] == 'anaglyph':
    (left, right) = cut_anaglyph(coords, im)

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
