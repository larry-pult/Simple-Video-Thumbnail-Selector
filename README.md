## Simple Video Thumbnail GIF Generator

### How To Set Up
1. Install Python 3.12 (maybe you can try with older versions, not sure)
2. Set up a new virtual environment (maybe you can use an existing one, not sure)
3. Install the packages from `requirements.txt`
4. Run `run_fastapi.bat` to run the app in localhost at port 8000
5. Refer to `main.py` to see how the endpoint works

### Description of Files
- `generator.py`: extracts audio from video, and does the thumbnail selection
- `main.py`: FastAPI app that hosts the API endpoint
- `run_fastapi.bat`: batch script to run FastAPI
- `api_testing_example.ipynb`: testing the API

### Approach
- Sample frames each second of the video, store it for later
  - If the scene of a frame is unchanged from the previous, skip it
  - For now, I use the absolute difference threshold method to detect scene change
- Select the frames with top 10 interestingness
  - Calculate interestingness with shannon entropy
- Create gif from the selected frames by sequentially joining them together and adding 1 second of interval between each
- Return the gif from the API, encoded in base 64

### Future Work
- Experiment with more metrics to define the interestingness of an image
- Experiment with more methods to detect scene change
- Create fade-in/fade-out transitions between keyframes in the GIF
- Experiment with more sampling rate