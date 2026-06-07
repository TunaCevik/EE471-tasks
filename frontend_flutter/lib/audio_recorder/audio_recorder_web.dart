import 'dart:async';
import 'dart:html' as html;
import 'dart:typed_data';
import 'audio_recorder.dart';

class WebAudioRecorder implements AudioRecorder {
  html.MediaRecorder? _mediaRecorder;
  final List<html.Blob> _chunks = [];
  Completer<List<int>?>? _completer;
  html.MediaStream? _stream;

  @override
  Future<void> start() async {
    _chunks.clear();
    try {
      final mediaDevices = html.window.navigator.mediaDevices;
      if (mediaDevices == null) {
        throw StateError('MediaDevices API is not supported in this browser.');
      }
      _stream = await mediaDevices.getUserMedia({'audio': true});
      _mediaRecorder = html.MediaRecorder(_stream!);
      
      _mediaRecorder!.addEventListener('dataavailable', (html.Event event) {
        try {
          final dynamic jsEvent = event;
          final html.Blob? blob = jsEvent.data;
          if (blob != null && blob.size > 0) {
            _chunks.add(blob);
          }
        } catch (e) {
          html.window.console.error('Error extracting audio chunk: $e');
        }
      });

      _mediaRecorder!.addEventListener('stop', (html.Event event) async {
        try {
          if (_chunks.isEmpty) {
            _completer?.complete(null);
            return;
          }
          final blob = html.Blob(_chunks, 'audio/wav');
          final reader = html.FileReader();
          reader.readAsArrayBuffer(blob);
          await reader.onLoadEnd.first;
          final bytes = reader.result as Uint8List;
          _completer?.complete(bytes.toList());
        } catch (e) {
          html.window.console.error('Error stopping recorder or reading blob: $e');
          _completer?.complete(null);
        } finally {
          // Stop all tracks
          _stream?.getTracks().forEach((track) => track.stop());
        }
      });

      _mediaRecorder!.start();
    } catch (e) {
      html.window.console.error('Error starting media recorder: $e');
      rethrow;
    }
  }

  @override
  Future<List<int>?> stop() async {
    _completer = Completer<List<int>?>();
    _mediaRecorder?.stop();
    return _completer!.future;
  }
}

AudioRecorder getAudioRecorder() => WebAudioRecorder();
