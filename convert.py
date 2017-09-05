import os
import glob
import sys
from bs4 import BeautifulSoup
from wand.image import Image

width = 64
height = 64

for char in sys.argv[1:]:

    if char is None:
        continue

    with open('dictionary.txt') as f:
        for i, line in enumerate(f):
            if 'character":"' + char + '"' in line:
                break

    baseFile = sorted(glob.glob('svgs/*.svg'))[i]
    name = baseFile[5:-4]

    tmpMap = 'tmp/' + name
    tmpFileNoExt = 'tmp/' + name + '/' + name
    resultMap = 'result/' + name
    resultFileNoExt = 'result/' + name + '/' + name

    if not os.path.isdir(resultMap):
        os.mkdir(resultMap)

    if not os.path.isdir(tmpMap):
        os.mkdir(tmpMap)

    # Edit the copied file
    file = open(baseFile, 'r')
    soup = BeautifulSoup(file, 'html.parser')

    # Bug with the html.parser changing viewBox to viewbox
    soup('svg')[0].attrs['viewBox'] = '0 0 1024 1024'

    # Remove the svg style drawing, we just want static images
    soup('g')[0].decompose()
    [tag.decompose() for tag in soup('style')]
    [tag.decompose() for tag in soup('clippath')]

    for tag in soup('path'):
        # Change the color to black
        tag['fill'] = 'black'

        # Remove the leftover path tags that we don't need
        if tag.get('id'):
            tag.decompose()

    # Set the data that we can later modify for each stroke
    file.close()

    # Create a file for each stroke in the tmpFile (each path element is 1 stroke) (note, it is counting reversed)
    for path in soup('path'):

        nr = "{0:0=2d}".format(len(soup('path')))
        tmp = open(tmpFileNoExt + '_' + nr + '.svg', 'w')
        tmp.write(soup.prettify())
        tmp.close()

        # Remove the last element in line, so we make the characters build up in reversed order
        soup('path')[-1].decompose()

    for file in glob.glob(os.path.join(tmpMap, '*.svg')):
        with Image(filename=file) as img:
            img.format = 'png'
            img.resize(width=width, height=height)
            img.save(filename='result/' + file[4:-4] + '.png')

    os.system('cd result/%s; convert * +append %s;' % (name, '../' + char + '.png'))

    # Show the id to easily find the image
    print(char + ": " + name)
