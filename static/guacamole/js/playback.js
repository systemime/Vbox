/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

function initExamplePlayer(record_file) {

    /**
     * The URL of the Guacamole session recording which should be played back.
     *
     * @constant
     * @type String
     */
    let RECORDING_URL = record_file;

    /**
     * The element which will contain the recording display.
     *
     * @type Element
     */
    let display = document.getElementById('display');

    /**
     * Play/pause toggle button.
     *
     * @type Element
     */
    let playPause = document.getElementById('play-pause');

    /**
     * Text status display indicating the current playback position within the
     * recording.
     *
     * @type Element
     */
    let position = document.getElementById('position');

    /**
     * Slider indicating the current playback position within the recording,
     * and allowing the user to change the playback position.
     *
     * @type Element
     */
    let positionSlider = document.getElementById('position-slider');

    /**
     * Text status display indicating the current length of the recording.
     *
     * @type Element
     */
    let duration = document.getElementById('duration');

    /**
     * The tunnel which should be used to download the Guacamole session
     * recording.
     *
     * @type Guacamole.Tunnel
     */
    let tunnel = new Guacamole.StaticHTTPTunnel(RECORDING_URL);

    /**
     * Guacamole.SessionRecording instance to be used to playback the session
     * recording.
     *
     * @type Guacamole.SessionRecording
     */
    let recording = new Guacamole.SessionRecording(tunnel);

    /**
     * The Guacamole.Display which displays the recording during playback.
     *
     * @type Guacamole.Display
     */
    let recordingDisplay = recording.getDisplay();

    /**
     * Converts the given number to a string, adding leading zeroes as necessary
     * to reach a specific minimum length.
     *
     * @param {Numer} num
     *     The number to convert to a string.
     *
     * @param {Number} minLength
     *     The minimum length of the resulting string, in characters.
     *
     * @returns {String}
     *     A string representation of the given number, with leading zeroes
     *     added as necessary to reach the specified minimum length.
     */
    let zeroPad = function zeroPad(num, minLength) {

        // Convert provided number to string
        let str = num.toString();

        // Add leading zeroes until string is long enough
        while (str.length < minLength)
            str = '0' + str;

        return str;

    };

    /**
     * Converts the given millisecond timestamp into a human-readable string in
     * MM:SS format.
     *
     * @param {Number} millis
     *     An arbitrary timestamp, in milliseconds.
     *
     * @returns {String}
     *     A human-readable string representation of the given timestamp, in
     *     MM:SS format.
     */
    let formatTime = function formatTime(millis) {

        // Calculate total number of whole seconds
        let totalSeconds = Math.floor(millis / 1000);

        // Split into seconds and minutes
        let seconds = totalSeconds % 60;
        let minutes = Math.floor(totalSeconds / 60);

        // Format seconds and minutes as MM:SS
        return zeroPad(minutes, 2) + ':' + zeroPad(seconds, 2);

    };

    // Add playback display to DOM
    display.appendChild(recordingDisplay.getElement());

    // Begin downloading the recording
    recording.connect();

    // If playing, the play/pause button should read "Pause"
    recording.onplay = function() {
        playPause.textContent = '暂停';
    };

    // If paused, the play/pause button should read "Play"
    recording.onpause = function() {
        playPause.textContent = '播放';
    };

    // Toggle play/pause when display or button are clicked
    display.onclick = playPause.onclick = function() {
        if (!recording.isPlaying())
            recording.play();
        else
            recording.pause();
    };

    // Fit display within containing div
    recordingDisplay.onresize = function displayResized(width, height) {

        // Do not scale if display has no width
        if (!width)
            return;

        // Scale display to fit width of container
        recordingDisplay.scale(display.offsetWidth / width);

    };

    // Update slider and status when playback position changes
    recording.onseek = function positionChanged(millis) {
        position.textContent = formatTime(millis);
        positionSlider.value = millis;
    };

    // Update slider and status when duration changes
    recording.onprogress = function durationChanged(millis) {
        duration.textContent = formatTime(millis);
        positionSlider.max = millis;
    };

    // Seek within recording if slider is moved
    positionSlider.onchange = function sliderPositionChanged() {
        recording.seek(positionSlider.value);
    };

}
