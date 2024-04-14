/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { onMounted, useState, useRef, Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LunchRecognitionDialog extends Component {
    setup() {
        this.rpc = useService("rpc");
        
        this.title = _t("Face Recognition");

        this.videoRef = useRef("video");
        this.imageRef = useRef("image");
        this.canvasRef = useRef("canvas");
        this.selectRef = useRef("select");

        this.notificationService = useService('notification');

        this.state = useState({
          videoElwidth: 0,
          videoElheight: 0,
          intervalID: false,
          match_employee_id : false,
          match_count : [],

          blinkMin : 10, // minimum duration of a valid blink
          blinkMax : 800,  // maximum duration of a valid blink
          blink : {
              start: 0,
              end: 0,
              time: 0,
          },

          faceCount : false,
          faceConfidence : false,
          blinkDetected : false,
          facingCenter : false,
          lookingCenter : false,
          antispoofCheck : false,
          livenessCheck  : false,
          headCheck : false,
          is_update_attendance: false,
          isInit: false,
        })

        this.faceapi = this.props.faceapi;
        this.descriptors = this.props.labeledFaceDescriptors;

        onMounted(async () => {
            await this.loadWebcam();            
        });  
    }
    loadWebcam(){
        var self = this;
        if (navigator.mediaDevices) {            
            var videoElement = this.videoRef.el;
            var videoSelect =this.selectRef.el;
            const selectors = [videoSelect]

            startStream();

            videoSelect.onchange = startStream;
            navigator.mediaDevices.enumerateDevices().then(gotDevices).catch(handleError);

            function startStream() {
                if (window.stream) {
                  window.stream.getTracks().forEach(track => {
                    track.stop();
                  });
                }
                const videoSource = videoSelect.value;
                const constraints = {
                  video: {deviceId: videoSource ? {exact: videoSource} : undefined}
                };
                navigator.mediaDevices.getUserMedia(constraints).then(gotStream).then(gotDevices).catch(handleError);
            }

            function gotStream(stream) {
                window.stream = stream; // make stream available to console
                videoElement.srcObject = stream;
                // Refresh button list in case labels have become available
                videoElement.onloadedmetadata = function(e) {
                    videoElement.play().then(function(){
                      self.detectionLoop();
                      self.drawLoop();
                    });
                    self.state.videoElwidth = videoElement.offsetWidth;
                    self.state.videoElheight = videoElement.offsetHeight;
                };
                return navigator.mediaDevices.enumerateDevices();
            }

            function gotDevices(deviceInfos) {
                // Handles being called several times to update labels. Preserve values.
                const values = selectors.map(select => select.value);
                selectors.forEach(select => {
                  while (select.firstChild) {
                    select.removeChild(select.firstChild);
                  }
                });
                for (let i = 0; i !== deviceInfos.length; ++i) {
                  const deviceInfo = deviceInfos[i];
                  const option = document.createElement('option');
                  option.value = deviceInfo.deviceId;
                  if (deviceInfo.kind === 'videoinput') {
                    option.text = deviceInfo.label || `camera ${videoSelect.length + 1}`;
                    videoSelect.appendChild(option);
                  } 
                  else {
                    // console.log('Some other kind of source/device: ', deviceInfo);
                  }
                }
                selectors.forEach((select, selectorIndex) => {
                  if (Array.prototype.slice.call(select.childNodes).some(n => n.value === values[selectorIndex])) {
                    select.value = values[selectorIndex];
                  }
                });
            }
            
            function handleError(error) {
                console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
            }               
        }
        else{
            this.notificationService.add(
              _t("https Failed: Warning! WEBCAM MAY ONLY WORKS WITH HTTPS CONNECTIONS. So your Odoo instance must be configured in https mode."), 
              { type: "danger" });
        }
    }
    async detectionLoop() {
      var self = this;
      var canvas =self.canvasRef.el;

      if (!canvas) {
          return;
      }
      var detectionFace = await self.detectionFace(canvas);
      if (detectionFace == 'break') {
          return;
      }

      return new Promise(function(resolve){
          self.detectionTimeout = setTimeout(function(){
              if(!self.state.isInit){
                  self.detectionLoop();
                  resolve();
              }                    
          });
      });
    }
    async drawLoop() {
      var self = this;

      var video = self.videoRef.el;
      var canvas =self.canvasRef.el;
      
      if (!canvas) {
          return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      var ctx = canvas.getContext('2d');
      
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      if (!video.paused) {
          const interpolated = await self.props.human.next(self.props.human.result);
          await self.props.human.draw.canvas(video, canvas);
          await self.props.human.draw.all(canvas, interpolated);
          
          //Validating Face
          const faceCount = self.props.human.result.face.length;
          if (faceCount === 1){
              self.state.faceCount = true;

              if ((self.props.human.result.face[0].faceScore || 0) > 0.6){
                self.state.faceConfidence  = true;
              }

              const gestures = Object.values(self.props.human.result.gesture).map((gesture) => gesture.gesture);

              if (gestures.includes('blink left eye') || gestures.includes('blink right eye')) {
                self.state.blink.start = self.props.human.now();
              }

              if (self.state.blink.start > 0 && !gestures.includes('blink left eye') && !gestures.includes('blink right eye')) {
                self.state.blink.end = self.props.human.now();
              }

              self.state.blinkDetected = self.state.blinkDetected || (Math.abs(self.state.blink.end - self.state.blink.start) > self.state.blinkMin && Math.abs(self.state.blink.end - self.state.blink.start) < self.state.blinkMax);
              if (self.state.blinkDetected && self.state.blink.time === 0) {
                self.state.blink.time = Math.trunc(self.state.blink.end - self.state.blink.start);
              }

              if (gestures.includes('facing center')){
                self.state.facingCenter = true;
              }

              if (gestures.includes('looking center')){
                self.state.lookingCenter = true;
              }

              if ((self.props.human.result.face[0].real || 0) > 0.6){
                self.state.antispoofCheck = true;
              }
              
              if ((self.props.human.result.face[0].live || 0) > 0.6){
                self.state.livenessCheck = true;
              }

              
              if (gestures.includes('head down') || gestures.includes('head up')) {
                self.state.headCheck = true;
              }
              
          }
      }

      return new Promise(function(resolve){
          self.drawTimeout = setTimeout(function(){
              if(!self.state.isInit){
                  self.drawLoop();
                  resolve();
              }
          },30);
      });
    }

    async detectionFace(canvas) {
          var self = this;

          const detect = await self.props.human.detect(canvas);
          self.props.human.draw.all(canvas, detect);

          if (!self.state.faceCount || !self.state.faceConfidence || !self.state.blinkDetected || !self.state.facingCenter || !self.state.lookingCenter|| !self.state.antispoofCheck || !self.state.livenessCheck || !self.state.headCheck){
              return;
          }

          if (detect && detect.face) {
              for (var face of detect.face) {
                  console.log("ll", self.descriptors)
                  const matchOptions = { order: 2, multiplier: 25, min: 0.2, max: 0.8 };
                  const descriptor = await self.descriptors.map((rec) => rec.descriptors).filter((desc) => desc.length > 0);
                  const match = await self.props.human.match.find(face.embedding, descriptor, matchOptions);

                  if ((match.similarity * 100).toFixed(2) >= 60) {
                      self.updaterecognition(self.descriptors[match.index].label, self.descriptors[match.index].name);
                      self.props.human.tf.dispose(face.tensor);
                      return 'break';
                  }
                  self.props.human.tf.dispose(face.tensor);
              }
          }
    }

    onClose() {
      var self = this;
      if (window.stream) {
        window.stream.getTracks().forEach(track => {
          track.stop();
        });
      }
      self.props.close && self.props.close();
    }

    async updaterecognition(user_id, user_name){
      var self = this;
      if (!self.state.is_update_attendance){
          self.props.updateRecognitionLunch({
            rdata: {
              'user_id': user_id,
              'user_name': user_name,
            },
          });
          self.state.is_update_attendance = true;
          if (window.stream) {
            window.stream.getTracks().forEach(track => {
                track.stop();
            });
        }
        this.props.close();
      }
    }
}
LunchRecognitionDialog.components = { Dialog };
LunchRecognitionDialog.template = "lunch_kiosk_mode_adv.LunchRecognitionDialog";
LunchRecognitionDialog.defaultProps = {};
LunchRecognitionDialog.props = {
  human: false,
  labeledFaceDescriptors : [],
}
