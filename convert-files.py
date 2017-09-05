import os
import glob
import re


for file in glob.glob(os.path.join('files', '*.txt')):

    output = []
    with open(file) as f:
        for line in f:
            result = re.search('\d+?\) ?(.)(?:\((.)\))?(:?.+?\n)?', line)
            if result:

                # Append <img src="file:///home/joris/bookimages/韓.png">
                def change_line(char):
                    global line
                    line = line.rstrip() + " <img src='file:///home/joris/bookimages/%s.png'>\n" % char

                def run_script(char):
                    os.system('python3.5 convert.py %s' % char)
                    pass

                if result.group(1):
                    change_line(result.group(1))
                    run_script(result.group(1))

                if result.group(2):
                    change_line(result.group(2))
                    run_script(result.group(2))

            output.append(line)

    f = open('result/files/%s' % file[6:], 'w+')
    f.writelines(output)
    f.close()
