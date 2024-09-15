import numpy as np
import cv2
import io
import requests
import mimetypes
import imageio
import base64
from urllib.parse import urlparse
from skimage.measure import shannon_entropy


def is_valid_video_link(link):
    """
    given a video url, check if it is a valid video file.
    if not, return False
    if yes, return True
    """
    try:
        response = requests.head(link, allow_redirects=True, timeout=10)
        
        # check content type header
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('video/'):
            return False, f"Not a video file. Content-Type: {content_type}"
        
        # check file extension
        parsed_url = urlparse(response.url)
        file_extension = parsed_url.path.split('.')[-1].lower()
        if mimetypes.guess_type(f"file.{file_extension}")[0] is None or not mimetypes.guess_type(f"file.{file_extension}")[0].startswith('video/'):
            return False, f"Invalid file extension: .{file_extension}"
        
        # check file size
        content_length = response.headers.get('Content-Length')
        if content_length is not None:
            file_size = int(content_length)
            if file_size < 1024:
                return False, f"File too small: {file_size} bytes"
            if file_size > 1024 * 1024 * 1024:
                return False, f"File too large: {file_size} bytes"
        
        return True, ""
    
    except requests.RequestException as e:
        return False, f"Request error: {str(e)}"
    

def is_scene_change(frame_1, frame_2, threshold=0.5):
    """
    given 2 video frames,
    use a simple algorithm to detect whether or not the scene is changed
    """
    assert frame_1.shape == frame_2.shape
    n, m, c = frame_1.shape

    abs_diff = np.abs(frame_1 - frame_2)
    avg_abs_diff = np.sum(abs_diff) / (n*m*c) / 255

    if avg_abs_diff > threshold:
        return True
    else:
        return False
    

def calculate_entropy(frame):
    return shannon_entropy(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))


def select_key_frames(link, max_frame_count=10):
    """
    given link (could be web url or directory),
    sample frames every second,
    detect whether or not the scene is changed (if not changed then ignore frame),
    and select key frames from the selected frames
    """
    cap = cv2.VideoCapture(link)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = int(frame_count / fps)

    # store frames and their entropies in a 2-tuple (frames, entropies)
    frames_and_entropies = list()
    prev_frame = None

    # sample frames each second in the video
    for i in range(duration):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fps * i)
        _, curr_frame = cap.read()

        # if no scene change, skip frame
        if prev_frame is not None and is_scene_change(prev_frame, curr_frame):
            continue
        
        # calculate the entropy of the frame
        entropy = calculate_entropy(curr_frame)

        # store the frame content and entropy as a 2-tuple
        frames_and_entropies.append((curr_frame, entropy))

    # sort frames_and_entropied based on entropy, descending
    frames_and_entropies.sort(key=lambda tup: tup[1], reverse=True)

    # return the top frames only
    return [tup[0] for tup in frames_and_entropies[:max_frame_count]]


def generate_thumbnail_from_key_frames(key_frames, interval_ms=1000):
    """
    given an array of video frames, output directory, and interval in seconds,
    create a gif of the video frames, with each frame having interval seconds, save it to output directory
    """
    # convert to RGB
    rgb_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in key_frames]
    
    buffer = io.BytesIO()

    # create the gif in "temp" directory
    imageio.mimsave(buffer, rgb_frames, format="gif", duration=interval_ms)

    return buffer.getvalue()


# for testing purposes
if __name__ == "__main__":
    print(f"file_example_MP4_480_1_5MG.mp4 is valid video : {is_valid_video_link("https://file-examples.com/storage/fe7060053866e6b63a04ca8/2017/04/file_example_MP4_480_1_5MG.mp4")}")
    print(f"https://www.google.com is valid video         : {is_valid_video_link('https://www.google.com')}")
    print("creating gif from ./example_video.mp4")
    key_frames = select_key_frames("./example_video.mp4")
    print("success")