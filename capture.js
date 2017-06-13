/*
 * Capture patronus video from site pottermore (https://my.pottermore.com/patronus).
 *
 * Use MediaRecorder to record canvas stream.
 * Reference:
 *   https://developers.google.com/web/updates/2016/01/mediarecorder
 *
 * Usage:
 *   1. Copy the entire snippet to chrome console and run.
 *   2. run `rec.start()` to start recording.
 *   3. run `rec.stop()` to stop recording.
 *   4. run `save()` to download recorded video.
 *
 */

var c = document.querySelector('canvas');
var stream = c.captureStream();
var options = {
    //videoBitsPerSecond: 2500000,
    mimeType: 'video/webm'
};
var rec = new MediaRecorder(stream, options);
var chunks = [];
rec.ondataavailable = function(e) {
    chunks.push(e.data);
    console.log(chunks.length);
};
var save = function() {
    var blob = new Blob(chunks, {
        type: 'video/webm'
    });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'test.webm';
    a.click();
};

// Minimum version.
var c = document.querySelector('canvas'); var stream = c.captureStream(); var options = { videoBitsPerSecond: 2500000, mimeType: 'video/webm' }; var rec = new MediaRecorder(stream, options); var chunks = []; rec.ondataavailable = function(e) { chunks.push(e.data); console.log(chunks.length); }; var save = function() { var blob = new Blob(chunks, { type: 'video/webm' }); var url = URL.createObjectURL(blob); var a = document.createElement('a'); a.href = url; a.download = 'test.webm'; a.click(); };
