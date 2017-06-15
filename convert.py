import os
import glob
import sys
import re
from bs4 import BeautifulSoup
from wand.image import Image


for char in sys.argv[1:]:

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
        tag['fill'] = 'lightgray'

        # Remove the leftover path tags that we don't need
        if tag.get('id'):
            tag.decompose()

    # Set the data that we can later modify for each stroke
    file.close()

    # a new canvas to draw the numbers in (the other one is flipped vertically)
    scale = 8
    g = soup.new_tag('g')
    g.attrs['transform'] = 'scale(%d)' % scale
    soup.svg.append(g)

    def add_numbers(g, element):
        coordinates = element['d']

        # The last number in the draw with an arc (Q) are the coordinates to get
        matches = re.findall('(?:(?:Q.\-?\d+.\-?\d+)|(?:L)).(\-?\d+).(\-?\d+)', coordinates)

        num_list = []
        for j, match in enumerate(matches):
            # A high X is bad, but a high Y is good, because 0,0 is bottom left and 1024,1024 is top right
            num_list.append((int(match[0]) + 124) * (1024 - (int(match[1]) + 124)))  # added 124 to negate the negative

        lowest = matches[num_list.index(min(num_list))]
        highest = matches[num_list.index(max(num_list))]

        # Most likely lowest should be A and highest should be B, but we might need to introduce more logic
        # 50 added here b/c a slightly raising line shouldn't matter
        if lowest[0] < highest[0] and (900 - int(lowest[1])) < (900 - int(highest[1])) + 50:
            a = lowest
            b = highest
        else:
            a = highest
            b = lowest

        text_a = soup.new_tag('text')
        text_a.attrs['x'] = int(a[0]) / scale
        text_a.attrs['y'] = (900 - int(a[1])) / scale
        text_a.attrs['stroke'] = 'blue'
        text_a.string = 'a'

        text_b = soup.new_tag('text')
        text_b.attrs['x'] = int(b[0]) / scale
        text_b.attrs['y'] = (900 - int(b[1])) / scale
        text_b.attrs['stroke'] = 'blue'
        text_b.string = 'b'

        get_offset(text_a=text_a, text_b=text_b)

        g.insert(1, text_a)
        g.insert(1, text_b)

        return g

    # We need to define the offset depending on the stroke direction, so the A and B don't get placed in a wrong place
    def get_offset(text_a, text_b):

        # The offset should be bigger when the length is smaller
        offset_x = 16 - (abs(text_a.attrs['x'] - text_b.attrs['x']) / 20)
        offset_y = 14 - (abs(text_a.attrs['y'] - text_b.attrs['y']) / 20)

        text_a.attrs['x'] += offset_x
        text_a.attrs['y'] -= offset_y  # Minus here

        text_b.attrs['x'] += offset_x
        text_b.attrs['y'] += offset_y

    # Create a file for each stroke in the tmpFile (each path element is 1 stroke) (note, it is counting reversed)
    for path in soup('path'):

        # Change the color of the last path and add numbers for that path
        g = add_numbers(g, soup('path')[-1])
        soup('path')[-1]['fill'] = 'black'

        tmp = open(tmpFileNoExt + '_' + str(len(soup('path'))) + '.svg', 'w')
        tmp.write(soup.prettify())
        tmp.close()

        # Remove the last element in line, so we make the characters build up in reversed order
        soup('path')[-1].decompose()
        # And remove the two numbers again for the next loop
        g.next_element.decompose()
        g.next_element.decompose()

    for file in glob.glob(os.path.join(tmpMap, '*.svg')):
        with Image(filename=file) as img:
            img.format = 'png'
            img.resize(width=128, height=128)
            img.save(filename='result/' + file[4:-4] + '.png')

    os.system('cd result/%s; convert * +append %s;' % (name, '../' + name + '.png'))

    # Show the id to easily find the image
    print(char + ": " + name)
