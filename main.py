import docker
from docker import errors
import threading, queue, time, uuid, tarfile, io, os

imageName = "josephaltmaier/vqgan:0.1"
containerName = "image_generator_%s" % (str(uuid.uuid4()))

downloadsFolder = f"{os.getenv('USERPROFILE')}\\Downloads"

def main():
	shutdownEvent = threading.Event()
	container = None
	try:
		client = docker.from_env()
		print("Starting VQGAN+CLIP Docker image...")
		container = startDockerContainer(client)
		while container.status == "created":
			time.sleep(3)
			container.reload()
		if container.status != "running":
			print("Failed to start docker image, exiting")
			return
		print("Docker image is running")

		promptQueue = queue.Queue()
		dockerThread = threading.Thread(target=dockerAsync, args=(shutdownEvent, container, promptQueue, ))
		dockerThread.daemon = True
		dockerThread.start()
		while True:
			prompt = input("Enter prompts here:\n")
			promptQueue.put(prompt)
			print("Pending prompts are:\n%s" % ("\n".join(list(promptQueue.queue))))

	except Exception as e:
		print(e)
		print("Shutting down")
		return
	finally:
		shutdownEvent.set()
		if container is not None:
			container.stop()

def startDockerContainer(client):
	ensureDockerImage(client)	
	return client.containers.run(imageName, "/bin/bash -c \"trap : TERM INT; sleep infinity & wait\"", name=containerName, detach=True, auto_remove=True)

def ensureDockerImage(client):
	images = client.images.list(imageName)
	if len(images) > 0:
		return
	print("Pulling image", flush=True)
	client.images.pull(imageName)

def dockerAsync(shutdownEvent, container, promptQueue):
	while True:
		if shutdownEvent.is_set():
			return
		try:
			prompt = promptQueue.get(timeout=1)
		except queue.Empty:
			continue
		print("Working on prompt \"%s\"..." % (prompt), flush=True)
		generateImage(container, prompt)
		if shutdownEvent.is_set():
			return
		print("Finished generating prompt, copying %s.png to your Downloads folder" % (prompt), flush=True)
		copyBack(container, prompt)

def generateImage(container, prompt):
	_, output = container.exec_run(cmd="/bin/sh -c \"cd /VQGAN-CLIP; conda run -n vqgan python generate.py -p '%s' -i 180 -s 512 512 -cd cpu\"" % (prompt), socket=True, demux=False)
	while True:
		bytesRec = output.recv(1024)
		if (len(bytesRec) == 0):
			return

def copyBack(container, prompt):
	try:
		tarBytes = bytearray()
		bits, _ = container.get_archive('/VQGAN-CLIP/output.png')
		for chunk in bits:
			tarBytes.extend(chunk)
	except errors.NotFound:	
		print("Could not copy output from docker image")
		return

	try:
		tar = tarfile.open(fileobj=io.BytesIO(tarBytes))
		path = downloadsFolder + "/%s.png" % (prompt)
		extractedFile = tar.extractfile(member="output.png")
		if extractedFile is None:
			print("Could not extract output.png from tar file")
			return

		with open(path, 'wb') as out:
			out.write(extractedFile.read())
	finally:
		if tar is not None:
			tar.close()

if __name__ == "__main__":
    main()