"""
# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
client = language.LanguageServiceClient()

# The text to analyze
text = u'Hello World!'
document = types.Document(
    content=text,
    type=enums.Document.Type.PLAIN_TEXT)

# Detects the sentiment of the text
sentiment = client.analyze_sentiment(document=document).document_sentiment

print('Text: {}'.format(text))
print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
"""

from google.cloud import speech_v1p1beta1 as speech
client = speech.SpeechClient()

speech_file = 'commercial_mono.wav'

with open(speech_file, 'rb') as audio_file:
    content = audio_file.read()

audio = speech.types.RecognitionAudio(content = content)

config = speech.types.RecognitionConfig(
    encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=8000,
    language_code='en-US',
    enable_speaker_diarization=True,
    diarization_speaker_count=2)

print('Waiting for operation to comple...')
response = client.recognize(config, audio)

result = response.results[-1]

words_info = result.alternatives[0].words

for word_info in words_info:
    print(u"word: '{}', speaker_tag: {}".format(word_info.word, word_info.speaker_tag))
