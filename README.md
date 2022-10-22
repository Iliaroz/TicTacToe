# TicTacToe

## Aim of project
The project is final project for course "BEEAP20A7 - Modern Technology Applications" part "Robotics" and "Pattern recognition"

## Description

## Installation



### Python and libraries

The project was tested in the environment:

* python 3.10.6

	installed libraries:

	|Library | Version |
	|--------|---------|
	|pip |	22.2.2 |
	|numpy |	1.23.3 |
	|PyQt6 |	6.4.0 |
	|opencv-contrib-python |	4.6.0.66 |
	|tensorflow |	2.9.2 |
	|protobuf |	3.19.4 |

### Object Detection API

Additionally there was installed TensorFlow Object Detection API:

commands for Windows:

```
# Make folder somewhere on your disk
mkdir tf-models
cd tf-models
git clone https://github.com/tensorflow/models.git
cd models/research
# Compile protos.
protoc object_detection/protos/*.proto --python_out=.
# Install TensorFlow Object Detection API.
cp object_detection/packages/tf2/setup.py .
python -m pip install .
```

For some reason, the builder.py file is missing from the protobuf package created from TensorFlow. A workaround is to simply copy the latest copy of builder.py from the protobuf repository into your local drive

```
cd ../..
curl -o builder.py https://raw.githubusercontent.com/protocolbuffers/protobuf/main/python/google/protobuf/internal/builder.py
# CHANGE in command below [PYTHON_INSTALLATION_PATH] to your path, ex C:/python310
cp builder.py [PYTHON_INSTALLATION_PATH]/Lib/site-packages/google/protobuf/internal/builder.py
```

You can test Object Detection API installation by command

```
# Test the installation.
python object_detection/builders/model_builder_tf2_test.py
```

In some cases you need to reinstall ```opencv-contrib-python``` , to do that run commands:

```
 pip uninstall opencv-python opencv-python-headless opencv-contrib-python
 pip install opencv-contrib-python
```

