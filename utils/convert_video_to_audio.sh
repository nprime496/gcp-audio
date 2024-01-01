#!/bin/bash

# Set the input file as the first argument
input=$1

# Check if the second argument is provided; if not, default to "output.mp3"
output=${2:-output.mp3}

# Run ffmpeg with the provided input and output
ffmpeg -i "$input" "$output"
