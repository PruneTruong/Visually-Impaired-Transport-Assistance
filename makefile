install_gpu:
	pip install -r requirements.txt --user
	pip install tensorflow-gpu==1.7 --user

install_cpu:
	pip install -r requirements.txt
	pip install tensorflow==1.7
