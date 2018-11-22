SplitChannels
============

A plug-in for Nion Swift¹ that can split the channels of an RBG image.

Installation and Requirements
=============================

Requirements
------------
* Python >= 3.5 (lower versions might work but are untested)
* numpy (should be already installed if you have Swift installed)

Installation
------------
The recommended way is to use git to clone the repository as this makes receiving updates easy:
```bash
git clone https://github.com/Brow71189/swift_workshop_18
```

If you do not want to use git you can also use github's "download as zip" function and extract the code afterwards.

Once you have the repository on your computer, enter the folder "SplitChannels" within swift_workshop_18 and run the following from a terminal:

```bash
python setup.py install
```

It is important to run this command with __exactly__ the python version that you use for running Swift. If you installed Swift according to the online documentation (https://nionswift.readthedocs.io/en/stable/installation.html#installation) you should run `conda activate nionswift` in your terminal before running the above command.

Usage
======

Within Swift you can execute the plug-in by clicking on Processing -> Split Channels. In the inspector panel you can then select which channel you want to view.


¹ www.nion.com/swift