# vqgan-ui

main.py pulls a Docker image with VQGAN + CLIP installed from https://github.com/nerdyrodent/VQGAN-CLIP, starts that image, and provides a simple (awful) command line interface to 
queue prompts.  When the image is finished generating an impage, main.py will copy the finished image to your Downloads folder.  All images are currently generated using the CPU 
because my GPU isn't fancy enough to make larger images.  All images are currently generated at 512x512 because that's usually what I want and I haven't made a nicer UI which 
will let you easily configure things yet.

Requirements:
Windows
Docker Desktop.  For installation instructions please see https://docs.docker.com/desktop/windows/install/
Python.  I'm using 3.10 in a virtual environemnt and haven't tried anything else.

Use instructions:
(optional) Create and activate a new Python virtual environment
pip install -r requirements.txt
python main.py

This should bring up a command prompt.  main.py will automatically check for, pull, and start the necessary Docker image.  Once main.py starting the Docker image you will be able 
to enter prompts.  They will be stored in a queue and generated in the order you entered them.  Finished images will be copied to your Downlaods directory and named using the 
prompt which generated the image
