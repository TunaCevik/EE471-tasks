import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart' as rec;
import 'audio_recorder.dart';

class IoAudioRecorder implements AudioRecorder {
  final _recorder = rec.AudioRecorder();
  String? _path;

  @override
  Future<void> start() async {
    if (await _recorder.hasPermission()) {
      final tempDir = await getTemporaryDirectory();
      _path = '${tempDir.path}/voice_temp.wav';
      
      // Delete old temp file if it exists
      final file = File(_path!);
      if (await file.exists()) {
        try {
          await file.delete();
        } catch (_) {}
      }

      await _recorder.start(
        const rec.RecordConfig(
          encoder: rec.AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),
        path: _path!,
      );
    } else {
      throw StateError('Microphone permission not granted');
    }
  }

  @override
  Future<List<int>?> stop() async {
    try {
      final path = await _recorder.stop();
      if (path == null) return null;
      final file = File(path);
      if (await file.exists()) {
        return await file.readAsBytes();
      }
    } catch (_) {}
    return null;
  }
}

AudioRecorder getAudioRecorder() => IoAudioRecorder();
