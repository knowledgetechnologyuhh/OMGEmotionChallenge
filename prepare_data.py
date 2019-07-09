from __future__ import print_function
import argparse
import os
import sys
import subprocess
import datetime

lastFailedLink = "" #Keep track of the last failed link

def get_formatted_time(seconds):
    return str(datetime.timedelta(seconds=seconds))

#    microsecond = int((seconds - int(seconds)) * 1000 * 1000)
#    int_seconds = int(seconds)
#    hour = int_seconds // 3600
#    minute = (int_seconds - hour * 3600) // 60
#    second = int_seconds - hour * 3600 - minute * 60
#    return "{:02}:{:02}:{:02}.{:03}".format(hour, minute, second, microsecond)

def dl_youtube(link, target_file):
    global lastFailedLink
    if lastFailedLink == link: #Don't try to get a video again if it failed last time
        return False
    p = subprocess.Popen(["youtube-dl",
                          "-f", "best",
                          "--merge-output-format", "mp4",
                          "--restrict-filenames",
                          "--socket-timeout", "20",
                          "-iwc",
                          "--write-info-json",
                          '--write-annotations',
                          '--prefer-ffmpeg',
                          link,
                          '-o', target_file]
                        )
    out, err = p.communicate()

    if not os.path.exists(target_file):
        print ("Video not available - skipping: ", link)
        lastFailedLink = link
        return False
    return True

def prepare_data(file, target_dir):
    temp_directory = os.path.abspath(os.path.join(target_dir, "youtube_videos_temp"))
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    print ("here")
    with open(file) as f:
        next(f)
        for l in f:
            l = l.strip()
            if len(l) > 0:
                link, start, end, video, utterance = l.split(',')[:5]

		#print "Link:", link

                result_dir = os.path.join(os.path.join(target_dir, video))
                if not os.path.exists(result_dir):
                    os.makedirs(result_dir)
                result_filename = os.path.abspath(os.path.join(result_dir, utterance))
                #dl video with youtube-dl

                result = True

                target_file = os.path.abspath(os.path.join(temp_directory, video + ".mp4"))
                if not os.path.exists(target_file):
                    result = dl_youtube(link, target_file)

                if result:
                    p = subprocess.call(["ffmpeg",
                                     "-y",
                                     "-i", target_file,
                                     "-ss", get_formatted_time(float(start)),
                                     "-c:v", "libx264", "-preset", "superfast",
                                     "-f", "mp4",
                                     "-c:a", "aac",
                                     "-to", get_formatted_time(float(end)),
                                     '-strict', '-2',
                                     result_filename],
                                    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-file", help = "Metadata file")
    parser.add_argument("--target-dir")

    opt = parser.parse_args()
    if not os.path.exists(opt.split_file):
        print("Cannot find split file")
        sys.exit(-1)
    if not os.path.exists(opt.target_dir):
        os.makedirs(opt.target_dir)
    else:
        print("Target dir already exists.")
        
    prepare_data(opt.split_file, opt.target_dir)
