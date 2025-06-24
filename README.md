# MNet

**MNet** is a software for scan a network (similarly to `nmap`) but with some features. The software is divided into two parts: the first one is the **Scanner** that scan a network and return a list of devices with their IP, MAC address and hostname. The second one is the **Parser** that parse the output of the scanner in a more human readable form.

The software is written in Python and use **Scapy** to send packets to the network and **Prompt_toolkit** to create a more user friendly interface, but is still in development.

You can try it out and if you find any bug, please report it to me. Give me help if you like.

## Testing the software

For develope this software I used a virtual environment, so I reccomend you to use too. If you want to use the software, you need to install the packages in the file `requirements.txt`. Then, you can run the `main.py` file.

I created a `run.sh` file to simplify the process of installing and running the software. You can run it with `./run.sh` or `./run.sh clean` to clean the virtual environment. Idk if it works on Windows, but it should work on Linux and MacOS.

P.S. Sorry for the bad english (I wanted to write this document by myself without help).