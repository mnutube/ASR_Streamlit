from espnet2.bin.asr_inference import Speech2Text
import soundfile
import sys
import os
import re
import time
import librosa

from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, jsonify


def init_model():
    asr_config = "./exp/asr_train_asr_transformer5.aihub_raw_bpe/config.yaml"
    lm_config = "./exp/lm_train_lm.aihub_bpe/config.yaml"

    asr_path = "./exp/asr_train_asr_transformer5.aihub_raw_bpe/valid.acc.ave.pth"
    lm_path = "./exp/lm_train_lm.aihub_bpe/valid.loss.ave.pth"

    # speech2text = Speech2Text(asr_config, asr_path, lm_config, lm_path, ctc_weight=0.0, lm_weight=0.0, nbest=1)
    # speech2text = Speech2Text(asr_config, asr_path, lm_config, lm_path, ctc_weight=0.0, lm_weight=0.4, beam_size=2, nbest=10, device='cpu')
    speech2text = Speech2Text(
        asr_config,
        asr_path,
        lm_config,
        lm_path,
        ctc_weight=0.3,
        lm_weight=0.0,
        beam_size=3,
        nbest=1,  # 1,
        device="cpu",  # "cuda",
    )

    return speech2text


def recognize(audio_path, speech2text):
    y, sr = librosa.load(audio_path, mono=True, sr=16000)
    yt, index = librosa.effects.trim(y, top_db=25)

    audio, rate = soundfile.read(audio_path)
    dur = len(audio) / rate
    print("audio : {:d} {:.2f}".format(len(audio), dur))

    start_trim, end_trim = index
    audio_trim = audio[start_trim:end_trim]
    dur_trim = len(audio_trim) / rate

    print("audio : {:.2f} --> {:.2f}".format(dur, dur_trim))

    start = time.time()
    ret = speech2text(audio)  # Return n-best list of recognized results
    # print(ret)
    end = time.time()

    hyp_sents = []

    for idx_hyp in range(len(ret)):
        hyp_sent, _, _, hyp = ret[idx_hyp]
        hyp_sents.append(hyp_sent)
        # print(hyp)
        print("[{}] ({}), {:.4f}".format(
            idx_hyp + 1, hyp_sent, hyp.score.item()))

    elapsed_time = end - start
    print("time : {:.8f} (sec.)".format(elapsed_time))

    rtf = elapsed_time / dur
    print("RTF: {:.2f}".format(rtf))

    start_time = start_trim / rate
    end_time = end_trim / rate
    return {
        "text": hyp_sents[0],
        "elapsedTime": elapsed_time,
        "voiceStartTime": start_time,
        "voiceEndTime": end_time,
        "audioDuration": dur
    }


app = Flask(__name__)
app.secret_key = b'_5#y2L"F43412123fi9Q8z\n\xec]/'
speech2text_model = init_model()


@app.route('/recognize', methods=["POST"])
def hello():
    if 'file' not in request.files:        
        return 'No file part', 400

    file = request.files['file']
    filepath = os.path.join('wavs', file.filename)
    file.save(filepath)

    try:    
        return recognize(filepath, speech2text_model)
    except err:
        print(err)
        return 'speech recognition failure', 500
    finally: 
        try:
            os.remove(filepath)
        except:
            print('file remove faild: ' + filepath)
            

    return recognize(filepath, speech2text_model)

@app.route('/run', methods=["GET"])
def test():
    test_dic_path = './test'
    if not os.path.isdir(test_dic_path):
        return 'The test directory does not exist.', 400

    output = []
    for path in os.listdir(test_dic_path):
        output.append(recognize(path, speech2text_model))

    return output