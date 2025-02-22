#!/bin/bash

# Install Git
sudo apt install git -y
git config --global user.name "******"
git config --global user.email "******"
ssh-keygen
cat /home/aryank1511/.ssh/id_ed25519.pub

# Setup Developer Directory
mkdir Developer
cd Developer/
git clone git@github.com:AryanK1511/server-programs.git

# Install Vim
sudo apt install vim

# Enable SSH
sudo apt install openssh-server
sudo systemctl status ssh
sudo systemctl enable ssh
sudo ufw allow ssh

# Install Python
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-venv
sudo apt install pipx
