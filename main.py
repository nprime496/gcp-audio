import argparse
import subprocess
from google.cloud import speech_v2 as speech
from google.cloud import storage
import os
from google.cloud.speech_v2.types import cloud_speech
from google.api_core import exceptions
import logging
import traceback
from dotenv import load_dotenv
import time

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def transcribe_model_selection_gcs(
    project_id: str, gcs_uri: str
) -> speech.RecognizeResponse:
    """Transcribes audio from a Google Cloud Storage URI.

    Args:
        project_id: The Google Cloud project ID.
        gcs_uri: The Google Cloud Storage URI.

    Returns:
        The RecognizeResponse.
    """
    logging.info(f"Transcribing {gcs_uri} in project {project_id}")

    # Instantiates a client
    client = speech.SpeechClient()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["ru-RU"],
        model="long",
    )

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)

    logging.info(file_metadata)

    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/global/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )

    # Record the start time
    start_time = time.time()

    # Transcribes the audio into text
    try:
        operation = client.batch_recognize(request=request)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=10000)

        # Record the end time
        end_time = time.time()

        # Calculate the time taken for translation
        translation_time = end_time - start_time
        logging.info(f"Time taken for translation: {translation_time} seconds")

        logging.info("Transcription begin:")
        for result in response.results[gcs_uri].transcript.results:
            print(f"{result.alternatives[0].transcript}")
        logging.info("Transcription end:")
        return response
    except Exception as e:
        # Handle any exceptions that may occur during the request
        logging.info("An error occurred during batch speech recognition")
        logging.error(f"An error occurred during batch speech recognition: {str(e)}")
        return None


def transcribe_model_selection_gc_v1(
    gcs_uri: str, model: str
) -> speech.RecognizeResponse:
    """Transcribe the given audio file asynchronously with the selected model."""
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        model=model,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    return response


def convert_to_audio(input_video: str, output_audio: str) -> None:
    """Convert input video file to audio file using a shell script."""
    try:
        subprocess.run(
            ["./utils/convert_video_to_audio.sh", input_video, output_audio],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        print(f"Conversion successful: {input_video} to {output_audio}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during conversion: {e}")
        print(f"Error Code: {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error: {e.stderr}")
    except FileNotFoundError:
        print("The convert_video_to_audio.sh script was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def upload_to_bucket(bucket_name: str, file_name: str) -> None:
    """Upload file to the configured bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        generation_match_precondition = 0

        blob.upload_from_filename(
            file_name, if_generation_match=generation_match_precondition
        )

        logging.info(f"File {file_name} uploaded to {bucket_name}.")

    except exceptions.PreconditionFailed as e:
        logging.info("Precondition Failed")
        logging.debug(f"Precondition Failed {e.message}")
        logging.info(
            "This might be due to generation-match precondition or other conditional failure. The file might already exist."
        )
    except exceptions.NotFound as e:
        logging.info(
            "Bucket or file not found. Ensure the bucket name and file path are correct."
        )
        logging.debug(e)
    except exceptions.Forbidden as e:
        logging.info(
            "Access denied. Ensure your credentials are correct and have sufficient permissions."
        )
        logging.debug(e)
    except exceptions.GoogleAPICallError as e:
        logging.info("API call failed")
        logging.debug(f"API call failed {e}")

    except Exception as e:
        logging.debug(f"An unexpected error occurred: {e}")
        traceback.print_exc()


def main() -> None:
    # TODO: extend range of supported video extensions

    parser = argparse.ArgumentParser(
        description="Process an audio file, upload to bucket, transcribe and save output."
    )
    parser.add_argument("input_file", type=str, help="Input MP4 or MP3 file")
    parser.add_argument("--output_file", type=str, help="Output file for transcription")
    parser.add_argument(
        "--bucket", type=str, required=True, help="Bucket name for uploading"
    )
    parser.add_argument(
        "--model", type=str, default="default", help="Model for transcription"
    )
    parser.add_argument(
        "--convert", action="store_true", help="Convert input from MP4 to MP3"
    )
    args = parser.parse_args()

    input_file = args.input_file
    need_conversion = args.convert or input_file.lower().endswith(".mp4")

    # Determine input file type and convert if necessary
    if need_conversion:
        if not input_file.lower().endswith(".mp4"):
            print(
                "Error: --convert is set but the file does not have an .mp4 extension"
            )
            return
        mp3_file = input_file.replace(".mp4", ".mp3")
        convert_to_audio(input_file, mp3_file)
    else:
        mp3_file = input_file

    # Rest of the code remains the same
    # Upload to bucket
    upload_to_bucket(args.bucket, mp3_file)
    gcs_uri = f"gs://{args.bucket}/{mp3_file}"

    # Transcribe
    PROJECT_ID = os.getenv("PROJECT_ID")
    if PROJECT_ID:
        response = transcribe_model_selection_gcs(PROJECT_ID, gcs_uri)
    else:
        raise ValueError("The 'PROJECT_ID' environment variable is not set.")

    # Output transcription
    output_file = (
        args.output_file
        if args.output_file
        else os.path.join("target", f"transcribed-{os.path.basename(input_file)}.txt")
    )
    with open(output_file, "w") as file:
        # for i, result in enumerate(response.results):
        for result in response.results[gcs_uri].transcript.results:
            # print(f"Transcript: {result.alternatives[0].transcript}")
            alternative = result.alternatives[0]
            file.write(f"{alternative.transcript}\n")


if __name__ == "__main__":
    main()
