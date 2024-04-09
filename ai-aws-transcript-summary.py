import boto3
import json
import sys
import time
import uuid
from jinja2 import Template

# Connect to Amazon Web Services (AWS)
session = boto3.Session(
    aws_access_key_id='REPLACE_THIS_WITH_YOUR_AWS_KEY_ID',
    aws_secret_access_key='REPLACE_THIS_WITH_YOUR_AWS_SECRET_ACCESS_KEY'
)

# Create a AWS S3 (Simple Storage Service) client
s3_client = session.client('s3', region_name='us-west-2')

# Upload the audio file to the AWS S3 bucket
bucket_name = 'REPLACE_THIS_WITH_YOUR_AWS_S3_BUCKET_NAME'
file_name = 'dialog.mp3'
s3_client.upload_file(file_name, bucket_name, file_name)

# Create a AWS Transcribe client
transcribe_client = session.client('transcribe', region_name='us-west-2')

# Create a job name with a Universally Unique IDentifier (UUID)
job_name = 'transcription-job-' + str(uuid.uuid4())

# Transcribe the audio file
response = transcribe_client.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': f's3://{bucket_name}/{file_name}'},
    MediaFormat='mp3',
    LanguageCode='en-US',
    OutputBucketName=bucket_name,
    Settings={
        'ShowSpeakerLabels': True,
        'MaxSpeakerLabels': 2
    }
)

# Wait for the transcription to reach the status COMPLETED or FAILED
while True:
    status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    time.sleep(2)

if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
    
    # Load the transcript from S3
    transcript_key = f"{job_name}.json"
    transcript_obj = s3_client.get_object(Bucket=bucket_name, Key=transcript_key)
    transcript_text = transcript_obj['Body'].read().decode('utf-8')
    transcript_json = json.loads(transcript_text)
    
    output_text = ""
    current_speaker = None
    
    items = transcript_json['results']['items']
    
    for item in items:
        
        speaker_label = item.get('speaker_label', None)
        content = item['alternatives'][0]['content']
        
        # Start the line with the speaker label
        if speaker_label is not None and speaker_label != current_speaker:
            current_speaker = speaker_label
            output_text += f"\n{current_speaker}: "
            
        # Add the speech content
        if item['type'] == 'punctuation':
            output_text = output_text.rstrip()
            
        output_text += f"{content} "
        
    # Save the transcript to a text file
    with open(f'{job_name}.txt', 'w') as f:
        f.write(output_text.strip())

elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':

    # Terminate the program
    sys.exit("The transcription failed.")

# Create a AWS Bedrock runtime client
bedrock_runtime = session.client('bedrock-runtime', region_name='us-west-2')

# Read the transcript text file
with open(f'{job_name}.txt', "r") as file:
    transcript = file.read()

# Read the prompt template file
with open('prompt_template.txt', "r") as file:
    template_string = file.read()

# Create a dictionary with the data for the prompt
data = {
    'transcript' : transcript
}

# Initialise Jinja
template = Template(template_string)

# Create a prompt for the LLM through Jinja
prompt = template.render(data)

# Set the arguments for the LLM (Amazon titan-text-express-v1)
kwargs = {
    "modelId": "amazon.titan-text-express-v1",
    "contentType": "application/json",
    "accept": "*/*",
    "body": json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 2048,
                "temperature": 0,
                "topP": 0.9
            }
        }
    )
}

# Invoke the LLM
response = bedrock_runtime.invoke_model(**kwargs)

# Get the LLM output text
response_body = json.loads(response.get('body').read())
generation = response_body['results'][0]['outputText'].strip()

# Save the LLM result to a JSON file
with open(f'result-{job_name}.json', 'w') as f:
    f.write(generation)

# Show the result
print(generation)
