#!/bin/bash

# Check if .gitconfig file exists, if not, create it
if [ ! -f ~/.gitconfig ]; then
    touch ~/.gitconfig
fi

# Check if .ssh directory exists, if not, create it
if [ ! -d ~/.ssh ]; then
    mkdir -p ~/.ssh
fi