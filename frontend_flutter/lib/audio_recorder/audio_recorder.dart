import 'audio_recorder_stub.dart'
    if (dart.library.html) 'audio_recorder_web.dart'
    if (dart.library.io) 'audio_recorder_io.dart';

abstract class AudioRecorder {
  factory AudioRecorder() => getAudioRecorder();
  Future<void> start();
  Future<List<int>?> stop();
}
