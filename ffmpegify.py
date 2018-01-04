import pathlib
import re
import sys
import subprocess

FRAME_RATE = 25
MAX_WIDTH = 1920    # Set to 0 for no maximuim
MAX_HEIGHT = 1080  # Set to 0 for no maximuim
CRF = 18
PRESET = "fast"

# TODO
# overwriting existing?
# couple of version in sub-menu for different codecs/qualities?
# name video with parent folder name?
# find and deal with broken edge cases 

def convert(path):
    file = pathlib.Path(path)
    stem = file.stem
    suffix = file.suffix
    standard = ['.jpg', '.jpeg', '.png', '.tiff', '.tif']
    gamma = ['.exr', '.tga']
    alltypes = standard + gamma

    if( suffix in alltypes ):
        l = len(stem)
        back = stem[::-1]
        # this could be changed to re.match()[0] which would match files like render-0004-hi.png ?
        # would also need to get the extra text between frame number and extension
        m = re.search( '\d+', back)
        # m = re.match( '\d+', back)
        if(m):
            # simple regex match - find digit from the end of the stem (its assumed frame numbers are the last part of a file name)
            sp = m.span(0)
            sp2 = [l-a for a in sp]
            sp2.reverse()

            # get zfill for frame num
            padding = sp2[1] - sp2[0]
            padstring = '%' + format(padding, '02') + 'd' # eg %05d

            # glob for other frames in the folder and find the first frame to use as start number
            preframepart = stem[0:sp2[0]]
            postframepart = stem[sp2[1]:]
            frames = sorted(file.parent.glob(preframepart + '*'))
            start_num = int(frames[0].name[sp2[0]:sp2[1]])

            # get absolute path to the input file and set the outputfile
            inputf = stem[0:sp2[0]] + padstring + postframepart + suffix
            inputf_abs = str(file.with_name(inputf))
            outputf = str(file.with_name( '_' + file.parent.name + "_video.mov" ))

            cmd = ['ffmpeg']
            cmd.extend(('-r', str(FRAME_RATE)))
            if(suffix in gamma):
                cmd.extend(('-gamma', '2.2'))
            cmd.extend(('-start_number', str(start_num).zfill(padding) ))
            cmd.extend(('-i', inputf_abs))
            cmd.extend(('-c:v', 'libx264'))
            cmd.extend(('-pix_fmt', 'yuv420p', '-crf', str(CRF), '-preset', 'fast'))
            # scale if exceeding max?
            # scale=w='if(gt(dar,854/480),min(854,iw*sar),2*trunc(iw*sar*oh/ih/2))':h='if(gt(dar,854/480),2*trunc(ih*ow/iw/sar/2),min(480,ih))'
            cmd.extend(('-vf', 'premultiply=inplace=1, scale=trunc(iw/2)*2:trunc(ih/2)*2'))
            cmd.append(outputf)
            subprocess.run(cmd)
        else:
            pass 
    else:
        print("Invalid file extension")

if __name__ == '__main__':
    convert(sys.argv[1])