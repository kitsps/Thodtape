# Thodtape Project

Get transcription text from your audio using Speech-to-Text service from multiple cloud providers, [Azure Cognitive services](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/overview), [Google Cloud Platform](https://cloud.google.com/speech-to-text), [iApp AI](https://ai.iapp.co.th/product/speech_to_text_asr) 


## Install prerequisite libraries
```
pip3 install azure-cognitiveservices-speech
pip3 install google.cloud
pip3 install google
pip3 install google-cloud-storage
pip3 install google-cloud-speech
pip3 install flask
pip3 install flask_wtf
pip3 install python-dotenv
```

## Config your credentail from cloud providers

```
cp .env.dist .env
cp gcp_key.json.dist gcp_key.json
```

## Configure your cloud credential in [.env]
```
#Azure Subscription Key
AZURE_SUBSCRIPTION_KEY=
#GCP SA Credentials
GOOGLE_APPLICATION_CREDENTIALS=gcp_key.json
PROJECT_ID=
BUCKET_NAME=
#iApp AI APIs Credentials
IAPP_APIKEY=
```

## Config GCP Service Account [gcp_key.json]
it needs to access your Google cloud storage (at least storage.objects.create, storage.objects.delete, storage.objects.get)
```
{
    "type": "service_account",
    "project_id": "",
    "private_key_id": "",
    "private_key": "",
    "client_email": "",
    "client_id": "",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": ""
  }
```

## Start Web service
```
python3 web.py
```

## How to use
 - select prefered audio language
 - select your audio file
 - click 'Upload File'

![alt text](https://git.bknix.co.th/git/kittinan/thodtape_project/raw/f600222fb935da54b68a52e99994fe65bc28afde/example/example_ui.png)
