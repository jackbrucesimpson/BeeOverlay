#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:     Overlay Video
# Purpose:  Uses OpenCV and Pandas to draw over a Video from data in a CSV file without saving
# Author:   Jack Simpson
# Email:    jack.simpson@anu.edu.au
# Created:  2015-02-06
#-------------------------------------------------------------------------------
# These modules are available in the Standard Library of Python
import os.path
import sys
# These modules come from third party libraries
import cv2
import pandas as pd

def read_group_data(path):
    sys.stderr.write('Loading %s\n' % path)
    data = pd.read_csv(path, comment='#') # skiprows=1
    group_by_frame = data.groupby('Frame', sort=True)
    frame_groups_dict = dict(list(group_by_frame))
    return frame_groups_dict

def draw_on_frame(drawing_frame, frame_group, prev_coords_on_frame):
    coords_from_frame = []

    #for prev_coord in prev_coords_on_frame:
        #cv2.circle(drawing_frame,(prev_coord[0], prev_coord[1]), 10, (255,0,0), -1)

    for i, value in frame_group['Frame'].iteritems():
        bee_id = frame_group['BeeID'][i]
        tag_type = frame_group['Tag'][i]
        x_coord = int(frame_group['X'][i])
        y_coord = int(frame_group['Y'][i])
        coords_from_frame.append((x_coord, y_coord))
        offset = 10
        cv2.putText(drawing_frame,
                str(tag_type), #bee_id
                (x_coord + offset, y_coord + offset),
                cv2.FONT_HERSHEY_DUPLEX,
                1, (255, 255, 255), 2)
        #cv2.circle(drawing_frame,(x_coord, y_coord), 25, (0,0,255), 2)


    return (drawing_frame, coords_from_frame)

def main():
    if len(sys.argv) != 4:
        sys.stderr.write('Usage: %s CSV VIDEO' % os.path.basename(sys.argv[0]))
        sys.exit(1)

    csv = sys.argv[1]
    frame_groups = read_group_data(csv)

    video = sys.argv[2]
    cap = cv2.VideoCapture(video)
    frames_to_skip = int(sys.argv[3]) * 25
    frame_count = 0

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4v',fourcc, 25, (1536, 864))

    all_prev_frames_coords = []

    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame_count < frames_to_skip:
            frame_count += 1
            if frame_count % 1500 == 0:
                print("Skipped %d out of %d" % (frame_count, frames_to_skip))
            continue

        if frame_count in frame_groups:
            frame_df = frame_groups[frame_count]
            frame, prev_frames_coords = draw_on_frame(frame, frame_df, all_prev_frames_coords)
            all_prev_frames_coords.extend(prev_frames_coords)

        small_frame = cv2.resize(frame, (1536, 864))  ### This could be command line options (see argparse module)
        cv2.imshow('frame', small_frame)
        if frame_count % 10 == 0:
            out.write(small_frame)

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

        frame_count += 1
        print(frame_count)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
