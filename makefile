install_gpu:
	pip install -r requirements.txt
	pip install tensorflow-gpu==1.6

install_cpu:
	pip install -r requirements.txt
	pip install tensorflow==1.6
