import streamlit as st
import numpy as np
import base64

# HTML과 JavaScript 코드
stt_html = """
    <div id="controls">
        <button id="recordButton">Start Recording</button>
        <button id="stopButton" disabled>Stop Recording</button>
    </div>
    <div id="formats">Format: WAV</div>
    <p><strong>Recordings:</strong></p>
    <ul id="recordingsList"></ul>

    <script>
        let recordButton, stopButton, recordingsList;
        let audioContext, gumStream, rec;

        window.onload = () => {
            recordButton = document.getElementById("recordButton");
            stopButton = document.getElementById("stopButton");
            recordingsList = document.getElementById("recordingsList");

            recordButton.addEventListener("click", startRecording);
            stopButton.addEventListener("click", stopRecording);
        };

        function startRecording() {
            recordButton.disabled = true;
            stopButton.disabled = false;

            navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                gumStream = stream;
                const input = audioContext.createMediaStreamSource(stream);
                rec = new Recorder(input, { numChannels: 1 });
                rec.record();
            }).catch((err) => {
                recordButton.disabled = false;
                stopButton.disabled = true;
            });
        }

        function stopRecording() {
            stopButton.disabled = true;
            recordButton.disabled = false;

            rec.stop();
            gumStream.getAudioTracks()[0].stop();

            rec.exportWAV((blob) => {
                const url = URL.createObjectURL(blob);
                const li = document.createElement("li");
                const au = document.createElement("audio");
                const link = document.createElement("a");

                au.controls = true;
                au.src = url;
                link.href = url;
                link.download = "recording.wav";
                link.innerHTML = "Download recording";
                li.appendChild(au);
                li.appendChild(link);
                recordingsList.appendChild(li);

                const reader = new FileReader();
                reader.readAsDataURL(blob);
                reader.onloadend = () => {
                    const base64AudioMessage = reader.result.split(",")[1];
                    const message = new MessageEvent("audioData", { data: base64AudioMessage });
                    window.dispatchEvent(message);
                };
            });
        }

        function downloadAudio(data, filename) {
            const blob = new Blob([data], { type: "audio/wav" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        }
    </script>

    <script src="https://cdn.rawgit.com/mattdiamond/Recorderjs/08e7abd9/dist/recorder.js"></script>
"""
if __name__ == '__main__':
    # HTML 및 JavaScript 코드 삽입
    st.components.v1.html(stt_html, height=600)

    # 이벤트 리스너로부터 오디오 데이터 수신
    audio_data = st.experimental_get_query_params().get("audioData", [None])[0]

    if audio_data:
        st.audio(base64.b64decode(audio_data), format="audio/wav")
