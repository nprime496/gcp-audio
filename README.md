# GCP Speech-to-Text Transcription Tool (API v2)

## Purpose

This tool is designed to provide an easy and efficient way to transcribe audio content into text by leveraging Google Cloud's powerful Speech-to-Text API. It automates the process of audio conversion, uploading to a Google Cloud Storage bucket, and transcription. The primary purpose is to aid in quickly transcribing large volumes of audio data with high accuracy, suitable for various applications such as content creation, subtitles, and more.

## Features

- Audio conversion from video to audio format.
- Automatic uploading of audio files to Google Cloud Storage.
- Transcription of audio using Google Cloud's Speech-to-Text API.
- Support for different language models and automatic detection of speech segments.

## Prerequisites

1. **Google Cloud Platform Account**: Have a project on GCP with Cloud Speech API enabled and a storage bucket created.
2. **Service Account**: Enough permissions to create a service account and manage Google Cloud resources.
3. **Google Cloud SDK**: Ensure that Google Cloud SDK is installed and initialized in your environment.
4. **Python Environment**: Python 3.x along with the `poetry` package manager to handle dependencies.

## Setup and Configuration

1. **Google Cloud Project and Service Account**:
   - Create or select a project in Google Cloud Platform.
   - Enable the Cloud Speech API for the project.
   - Create a service account with appropriate roles and download the JSON key file.

2. **Environment Variables**:
   - Rename the downloaded JSON key file to `google_credentials.json` and place it in your project directory.
   - Create a `.env` file in your project directory and add the following variables:
     ```
     GOOGLE_APPLICATION_CREDENTIALS=google_credentials.json
     PROJECT_ID=your_gcp_project_id
     ```

3. **Dependency Installation**:
   - Run `poetry install` to install all the necessary dependencies.

## Usage

1. **Prepare Your Audio/Video Files**: Ensure your files are in the correct format and accessible.

2. **Running the Script**: Use the command line to run the script with appropriate arguments:
   ```
   python main.py input_file --output_file=transcription.txt --bucket=my-bucket --model=default --convert
   ```
   - `input_file`: Path to your input audio or video file.
   - `--output_file`: (Optional) Path for the output transcription text file.
   - `--bucket`: Name of your Google Cloud Storage bucket.
   - `--model`: (Optional) Specify the model for transcription.
   - `--convert`: (Optional) Flag to convert input from MP4 to MP3.

## Improvements and Ideas

- **Support for More Audio Formats**: Extend the script to handle various audio formats.
- **Enhanced Error Handling**: Implement robust error handling and logging for better debugging and user feedback.
- **Interactive CLI**: Develop an interactive CLI to guide users through the transcription process step-by-step.
- **Web Interface**: Create a simple web interface for users to upload files, initiate transcription, and view results.
- **Batch Processing**: Add support for batch processing of multiple files for efficient bulk transcription.
- **Information extraction improvement**:  Add support for timestamps along with transcriptions.

## References

https://cloud.google.com/speech-to-text/v2/docs/batch-recognize 
