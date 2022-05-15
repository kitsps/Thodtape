import re
import requests
import json
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from google.cloud import storage

#from azure_python_client import azure_speech_recognize_continuous_from_file
import time
import wave
import string
import json
import os

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NTBkODJmODM5YjIyZmUyMTMzMDgyOTljM2U2N2U0ZDM0OGI3YmViYSAgLQo='
app.config['UPLOAD_FOLDER'] = 'static/files'

app.config['AZURE_SUBSCRIPTION_KEY'] = os.environ.get("AZURE_SUBSCRIPTION_KEY") 

app.config['PROJECT_ID'] = os.environ.get("PROJECT_ID")
app.config['BUCKET_NAME'] = os.environ.get("BUCKET_NAME")

app.config['IAPP_APIKEY'] = os.environ.get("IAPP_APIKEY")

# Set environment variables
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


def get_azure_access_token(subscription_key):
    fetch_token_url = 'https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)
    #print(access_token)

    #write file
    f = open("azure_access_token", "w")
    f.write(access_token)
    f.close()


def transcribe_azure (AZURE_SUBSCRIPTION_KEY, file, Language):

    #Enable/disable azure access token
    #get_azure_access_token(AZURE_SUBSCRIPTION_KEY)

    language_code = "en-US"

    if (Language == "TH"):
        language_code = "th-TH"
    else:
        language_code = "en-US"

    #url = "https://southeastasia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US"
    url = "https://southeastasia.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language="+language_code

    headers = {
    'Content-type': 'audio/wav;codec="audio/pcm";',
    'Ocp-Apim-Subscription-Key': AZURE_SUBSCRIPTION_KEY,
    # OR 'Authorization: Bearer ACCESS_TOKEN'
    }

    #with open('{FILE_PATH\\Welcome.wav','rb') as payload:
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)),'rb') as payload:
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

        if response.status_code == 200:
            #response.text = {"RecognitionStatus":"Success","DisplayText":"สวัสดีครับน้องไข่ต้มเสียงเด็กผู้ชายมาแล้วฮะ","Offset":300000,"Duration":49100000}
            full_json = json.loads(response.text)
            return full_json["DisplayText"]
    
    return "Error"

def azure_speech_recognize_once_from_file( AZURE_SUBSCRIPTION_KEY, service_region, file, Language):
    language_code = "en-US"

    if (Language == "TH"):
        language_code = "th-TH"
    else:
        language_code = "en-US"

    """performs one-shot speech recognition with input from an audio file"""
    # <SpeechRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SUBSCRIPTION_KEY , region=service_region)
    #audio_config = speechsdk.audio.AudioConfig(filename=weatherfilename)
    audio_config = speechsdk.audio.AudioConfig(filename= os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))


    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language_code, audio_config=audio_config)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = speech_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
    # </SpeechRecognitionWithFile>

def azure_speech_recognize_continuous_from_file(AZURE_SUBSCRIPTION_KEY, service_region, file, Language):
    all_result = []
    all_result_text = ""

    language_code = "en-US"

    if (Language == "TH"):
        language_code = "th-TH"
    else:
        language_code = "en-US"

    """performs continuous speech recognition with input from an audio file"""
    # <SpeechContinuousRecognitionWithFile>
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SUBSCRIPTION_KEY, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename= os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config, language=language_code)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True
        #print ()
        #print (type(evt))
        #print ('Final Result = {}'.format(evt))
        #return evt.result
        # print (speech_recognizer.recognize_once())
        # return speech_recognizer.recognize_once()\
        #speech_recognizer.recognize_once_async.__get__

    # Connect callbacks to the events fired by the speech recognizer
    # speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    # speech_recognizer.recognized.connect(lambda evt: (print('RECOGNIZED: {}'.format(evt))))
    # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    #Collect result for return
    speech_recognizer.recognized.connect(lambda evt : all_result.append( evt.result.text) )

    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)
        

    speech_recognizer.stop_continuous_recognition()
    # </SpeechContinuousRecognitionWithFile>

    for element in all_result:
        all_result_text += element
    return all_result_text

def transcribe_gcs_with_word_time_offsets(Language, gcs_uri):
    """Transcribe the given audio file asynchronously and output the word time
    offsets."""
    from google.cloud import speech

    all_transcript = ""
    language_code = "en-US"

    if (Language == "TH"):
        language_code = "th-TH"
    else:
        language_code = "en-US"

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)

    if (gcs_uri.endswith('.wav') | gcs_uri.endswith('.WAV')): 
        config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        #sample_rate_hertz=16000,
        audio_channel_count=2,
        language_code=language_code,
        #enable_word_time_offsets=True,
    )
    elif (gcs_uri.endswith('.flac') | gcs_uri.endswith('.FLAC')): 
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
            #encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=16000,
            audio_channel_count=2,
            language_code=language_code,
            #enable_word_time_offsets=True,
        )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    result = operation.result(timeout=90)

    for result in result.results:
        alternative = result.alternatives[0]
        #print("Transcript: {}".format(alternative.transcript))
        #print("Confidence: {}".format(alternative.confidence))
        all_transcript += format(alternative.transcript)+"\n"

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time

            print(
                f"Word: {word}, start_time: {start_time.total_seconds()}, end_time: {end_time.total_seconds()}"
            )

    #return Transcript text   
    #return format(alternative.transcript)
    return all_transcript    


def transcribe_iapp(IAPP_APIKEY, file):

    url = "https://api.iapp.co.th/asr"

    payload={}
    files=[
    #('file',( Filename, open('../static/files/'+Filename,'rb'),'audio/mpeg'))
    ('file',( file.filename , open(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)),'rb'),'audio/mpeg'))
    ]
    headers = {
    'apikey': IAPP_APIKEY
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    #response.text = {"text":"\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e35\u0e04\u0e23\u0e31\u0e1a\u0e19\u0e49\u0e2d\u0e07\u0e44\u0e02\u0e48\u0e15\u0e49\u0e21\u0e40\u0e2a\u0e35\u0e22\u0e07\u0e40\u0e14\u0e47\u0e01\u0e1c\u0e39\u0e49\u0e0a\u0e32\u0e22\u0e21\u0e32\u0e41\u0e25\u0e49\u0e27\u0e2e\u0e30"} 
    #print(response.text)
    full_json = json.loads(response.text)
    return full_json["text"]
    

def upload_to_google_cloud_storage(project, bucket, destination_blob_name, file):
    #client = storage.Client(credentials=credentials, project='myproject')
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket)
    #blob = bucket.blob('example_filename.txt')
    #blob = bucket.blob(file.filename)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
    #blob.upload_from_file (file)
    #blob.upload_from_string( file.read(),  content_type=file.content_type )


def upload_blob(project, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)   

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():

    Filename = ''
    Language = ''

    azure_translate = ''

    gcp_translate = ''

    iapp_translate = ''



    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        
        form_data = request.form.to_dict()
        Language = form_data['lang']
        
        #Patameters
        Filename = file.filename

        #debug
        #print (form_data.items())
        #print (form_data.to_dict())
        #print (form.file.filename)

        ##Call Azure transcribe
        #azure_translate = transcribe_azure (app.config['AZURE_SUBSCRIPTION_KEY'] , file, Language )
        ##azure_translate = azure_speech_recognize_once_from_file()
        #azure_translate = azure_speech_recognize_once_from_file (app.config['AZURE_SUBSCRIPTION_KEY'], 'southeastasia', file, Language)
        azure_translate = azure_speech_recognize_continuous_from_file (app.config['AZURE_SUBSCRIPTION_KEY'], 'southeastasia', file, Language)
        
        ##upload file to Google cloud storage
        upload_to_google_cloud_storage( app.config['PROJECT_ID'], app.config['BUCKET_NAME'], file.filename, file) 
        
        
        ##Call GPC transcribe
        gcp_translate = transcribe_gcs_with_word_time_offsets(Language, "gs://"+app.config['BUCKET_NAME']+"/"+file.filename)
        
        ##Call iApp transcribe
        iapp_translate = transcribe_iapp (app.config['IAPP_APIKEY'], file)

        
        #render_template('index.html')
        #return "File has been uploaded."



    return render_template('index.html', form=form, Filename=Filename, Language=Language, gcp_translate=gcp_translate, iapp_translate=iapp_translate, azure_translate=azure_translate)

if __name__ == '__main__':
    app.run(debug=True)