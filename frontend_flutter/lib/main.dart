import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:http/http.dart' as http;
import 'audio_recorder/audio_recorder.dart';



void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RoboMunch - AI Artist Studio',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFFD46A36),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFD46A36),
          secondary: Color(0xFFFF8C42),
          surface: Color(0xFF1C1310),
        ),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
      ),
      home: const RoboMunchHome(),
    );
  }
}

class RoboMunchHome extends StatefulWidget {
  const RoboMunchHome({super.key});

  @override
  State<RoboMunchHome> createState() => _RoboMunchHomeState();
}

class _RoboMunchHomeState extends State<RoboMunchHome> {
  // Config state
  final TextEditingController _ipController = TextEditingController(text: '192.168.1.100');
  final TextEditingController _portController = TextEditingController(text: '8000');
  
  // Cloud VM Config state
  final TextEditingController _cloudIpController = TextEditingController(text: 'YOUR-VM-IP');
  final TextEditingController _cloudPortController = TextEditingController(text: '8000');
  bool _isProcessingCloud = false;
  
  // Image Generation state
  final TextEditingController _promptController = TextEditingController();
  Uint8List? _generatedImageBytes;
  bool _isGeneratingImage = false;
  String? _imageError;

  // Chat state
  final TextEditingController _chatInputController = TextEditingController();
  final ScrollController _chatScrollController = ScrollController();
  final List<Map<String, String>> _messages = [
    {'sender': 'MUNCH', 'text': 'Hello! I am Robo Munch. What shall we create today?'},
  ];
  String _conversationHistory = '';
  bool _isSendingMessage = false;

  // Speech-to-Text state
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _ipController.dispose();
    _portController.dispose();
    _cloudIpController.dispose();
    _cloudPortController.dispose();
    _promptController.dispose();
    _chatInputController.dispose();
    _chatScrollController.dispose();
    super.dispose();
  }

  String get _apiBase {
    final ip = _ipController.text.trim();
    final port = _portController.text.trim();
    return 'http://$ip:$port/api';
  }

  void _toggleListening() async {
    try {
      if (_isListening) {
        setState(() {
          _isListening = false;
        });

        // Show status that we are transcribing
        setState(() {
          _chatInputController.text = "Transcribing audio...";
        });

        final audioBytes = await _audioRecorder.stop();
        if (audioBytes == null || audioBytes.isEmpty) {
          setState(() {
            _chatInputController.clear();
          });
          return;
        }

        // Send to local Whisper-tiny endpoint
        final uri = Uri.parse('$_apiBase/speech-to-text');
        final request = http.MultipartRequest('POST', uri);
        request.files.add(
          http.MultipartFile.fromBytes(
            'audio',
            audioBytes,
            filename: 'voice.wav',
          ),
        );

        final streamedResponse = await request.send();
        final response = await http.Response.fromStream(streamedResponse);

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final text = data['text'] ?? '';
          setState(() {
            _chatInputController.text = text.trim();
          });
        } else {
          setState(() {
            _chatInputController.clear();
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Speech to text failed (status: ${response.statusCode})')),
            );
          }
        }
      } else {
        setState(() {
          _isListening = true;
          _chatInputController.text = "Listening...";
        });
        await _audioRecorder.start();
      }
    } catch (e) {
      debugPrint("Speech recognition error: $e");
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Speech recognition error: ${e.toString()}')),
        );
      }
      setState(() {
        _isListening = false;
        _chatInputController.clear();
      });
      // Ensure recorder is stopped on error
      try {
        await _audioRecorder.stop();
      } catch (_) {}
    }
  }

  Future<void> _generateImage() async {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) return;

    setState(() {
      _isGeneratingImage = true;
      _imageError = null;
      _generatedImageBytes = null;
    });

    try {
      final request = http.MultipartRequest('POST', Uri.parse('$_apiBase/generate-image'));
      request.fields['prompt'] = prompt;

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _generatedImageBytes = response.bodyBytes;
        });
      } else {
        final errorMsg = _tryParseError(response.body);
        setState(() {
          _imageError = 'Failed: $errorMsg';
        });
      }
    } catch (e) {
      setState(() {
        _imageError = 'Connection error. Check backend server IP.';
      });
    } finally {
      setState(() {
        _isGeneratingImage = false;
      });
    }
  }

  Future<void> _processCloudImage(String action) async {
    if (_generatedImageBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please generate an image first in the Art Studio!')),
      );
      return;
    }

    setState(() {
      _isProcessingCloud = true;
      _imageError = null;
    });

    try {
      final cloudIp = _cloudIpController.text.trim();
      final cloudPort = _cloudPortController.text.trim();
      final urlPath = action == 'resolution' ? 'get/resolution' : 'convert/grayscale';
      final uri = Uri.parse('http://$cloudIp:$cloudPort/$urlPath');

      final request = http.MultipartRequest('POST', uri);
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          _generatedImageBytes!,
          filename: 'artwork.png',
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        if (action == 'resolution') {
          final data = jsonDecode(response.body);
          final res = data['resolution'] ?? 'unknown';
          if (mounted) {
            showDialog(
              context: context,
              builder: (context) => AlertDialog(
                backgroundColor: const Color(0xFF1C1310),
                title: const Text('Image Resolution', style: TextStyle(color: Colors.white)),
                content: Text('The cloud server reported the resolution is: $res', style: const TextStyle(color: Colors.grey)),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('OK', style: TextStyle(color: Color(0xFFD46A36))),
                  ),
                ],
              ),
            );
          }
        } else {
          // Grayscale conversion
          setState(() {
            _generatedImageBytes = response.bodyBytes;
          });
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Image successfully converted to grayscale by Cloud VM!')),
            );
          }
        }
      } else {
        setState(() {
          _imageError = 'Cloud VM error: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _imageError = 'Failed to connect to Cloud VM. Check IP & Port settings.';
      });
    } finally {
      setState(() {
        _isProcessingCloud = false;
      });
    }
  }

  Future<void> _sendMessage() async {
    final text = _chatInputController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'sender': 'YOU', 'text': text});
      _chatInputController.clear();
      _isSendingMessage = true;
    });
    _scrollToBottom();

    try {
      final request = http.MultipartRequest('POST', Uri.parse('$_apiBase/chat'));
      request.fields['message'] = text;
      request.fields['history'] = _conversationHistory;

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final reply = data['reply'] ?? "I'm speechless!";
        
        setState(() {
          _messages.add({'sender': 'MUNCH', 'text': reply});
          _conversationHistory += '\nYOU: $text\nMUNCH: $reply';
        });
      } else {
        setState(() {
          _messages.add({'sender': 'SYSTEM', 'text': 'Error: Server returned status ${response.statusCode}'});
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({'sender': 'SYSTEM', 'text': 'Failed to connect. Check backend server IP.'});
      });
    } finally {
      setState(() {
        _isSendingMessage = false;
      });
      _scrollToBottom();
    }
  }

  String _tryParseError(String responseBody) {
    try {
      final decoded = jsonDecode(responseBody);
      return decoded['error'] ?? 'Unknown error';
    } catch (_) {
      return 'Server error';
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_chatScrollController.hasClients) {
        _chatScrollController.animateTo(
          _chatScrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Color(0xFF121212),
              Color(0xFF2A1B15),
              Color(0xFFD46A36),
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            stops: [0.0, 0.5, 1.0],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header & Logo
              _buildHeader(),
              
              // Network Settings Configuration (Collapsible)
              _buildNetworkConfig(),

              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: Column(
                    children: [
                      // Art Studio Section
                      _buildArtStudioSection(),
                      
                      const SizedBox(height: 24.0),
                      
                      // Chat Studio Section
                      _buildChatStudioSection(),
                      
                      const SizedBox(height: 16.0),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          RichText(
            text: TextSpan(
              style: GoogleFonts.playfairDisplay(
                fontSize: 28.0,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.0,
                color: const Color(0xFFF0F0F0),
              ),
              children: const [
                TextSpan(text: 'ROBO '),
                TextSpan(
                  text: 'MUNCH',
                  style: TextStyle(
                    color: Color(0xFFD46A36),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFFD46A36), width: 2),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFD46A36).withOpacity(0.4),
                  blurRadius: 12.0,
                  spreadRadius: 2.0,
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(27),
              child: Image.asset(
                'assets/images/image 30.png',
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    color: const Color(0xFF1C1310),
                    child: const Icon(
                      Icons.smart_toy_rounded,
                      color: Color(0xFFD46A36),
                      size: 28,
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNetworkConfig() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.3),
        borderRadius: BorderRadius.circular(16.0),
        border: Border.all(color: const Color(0xFFD46A36).withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.wifi, color: Color(0xFFD46A36), size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Local Host:',
                  style: TextStyle(color: Colors.grey[400], fontSize: 13),
                ),
              ),
              SizedBox(
                width: 120,
                height: 32,
                child: TextField(
                  controller: _ipController,
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    hintText: 'IP Address',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: const Color(0xFF1C1310),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide(color: Colors.grey[800]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: const BorderSide(color: Color(0xFFD46A36)),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 6),
              const Text(':', style: TextStyle(color: Colors.white)),
              const SizedBox(width: 6),
              SizedBox(
                width: 60,
                height: 32,
                child: TextField(
                  controller: _portController,
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    hintText: 'Port',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: const Color(0xFF1C1310),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide(color: Colors.grey[800]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: const BorderSide(color: Color(0xFFD46A36)),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.cloud_outlined, color: Color(0xFFD46A36), size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Cloud Host:',
                  style: TextStyle(color: Colors.grey[400], fontSize: 13),
                ),
              ),
              SizedBox(
                width: 120,
                height: 32,
                child: TextField(
                  controller: _cloudIpController,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    hintText: 'Cloud IP',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: const Color(0xFF1C1310),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide(color: Colors.grey[800]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: const BorderSide(color: Color(0xFFD46A36)),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 6),
              const Text(':', style: TextStyle(color: Colors.white)),
              const SizedBox(width: 6),
              SizedBox(
                width: 60,
                height: 32,
                child: TextField(
                  controller: _cloudPortController,
                  textAlign: TextAlign.center,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(fontSize: 12, color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    hintText: 'Port',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: const Color(0xFF1C1310),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: BorderSide(color: Colors.grey[800]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8.0),
                      borderSide: const BorderSide(color: Color(0xFFD46A36)),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildArtStudioSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.25),
        borderRadius: BorderRadius.circular(24.0),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Text(
              'Art Studio',
              style: GoogleFonts.playfairDisplay(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 12.0),
          
          // Image Output Box
          Container(
            width: double.infinity,
            height: 220,
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.4),
              borderRadius: BorderRadius.circular(16.0),
              border: Border.all(color: Colors.white.withOpacity(0.08)),
            ),
            clipBehavior: Clip.antiAlias,
            child: Stack(
              alignment: Alignment.center,
              children: [
                if (_generatedImageBytes == null && !_isGeneratingImage && _imageError == null)
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.image_outlined, size: 48, color: Colors.grey[600]),
                      const SizedBox(height: 8),
                      Text(
                        'Your artwork will appear here',
                        style: TextStyle(color: Colors.grey[500], fontSize: 14),
                      ),
                    ],
                  ),
                if (_generatedImageBytes != null)
                  Image.memory(
                    _generatedImageBytes!,
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: double.infinity,
                  ),
                if (_imageError != null && !_isGeneratingImage)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0),
                    child: Text(
                      _imageError!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                    ),
                  ),
                if (_isGeneratingImage)
                  Container(
                    color: Colors.black.withOpacity(0.6),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFD46A36)),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'Generating Masterpiece...',
                            style: GoogleFonts.inter(
                              color: const Color(0xFFD46A36),
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12.0),
          
          // Prompt Input and Paint button
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFF1C1310).withOpacity(0.8),
              borderRadius: BorderRadius.circular(16.0),
              border: Border.all(color: const Color(0xFFD46A36).withOpacity(0.2)),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 4.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _promptController,
                    maxLines: 2,
                    minLines: 1,
                    style: const TextStyle(fontSize: 14, color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Type your prompt here.',
                      hintStyle: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(vertical: 8.0),
                    ),
                  ),
                ),
                GestureDetector(
                  onTap: _isGeneratingImage ? null : _generateImage,
                  child: Container(
                    width: 38,
                    height: 38,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFD46A36), Color(0xFFFF8C42)],
                      ),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFD46A36).withOpacity(0.4),
                          blurRadius: 8.0,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Image.asset(
                        'assets/images/image 31.png',
                        width: 18,
                        height: 18,
                        color: Colors.white,
                        errorBuilder: (context, error, stackTrace) {
                          return const Icon(Icons.brush, color: Colors.white, size: 18);
                        },
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12.0),
          Row(
            children: [
              Expanded(
                child: GestureDetector(
                  onTap: _isProcessingCloud ? null : () => _processCloudImage('grayscale'),
                  child: Container(
                    height: 40,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: _isProcessingCloud
                            ? [Colors.grey[800]!, Colors.grey[700]!]
                            : [const Color(0xFFD46A36), const Color(0xFFD46A36).withOpacity(0.6)],
                      ),
                      borderRadius: BorderRadius.circular(12.0),
                      boxShadow: [
                        if (!_isProcessingCloud)
                          BoxShadow(
                            color: const Color(0xFFD46A36).withOpacity(0.2),
                            blurRadius: 6.0,
                            offset: const Offset(0, 2),
                          ),
                      ],
                    ),
                    child: Center(
                      child: _isProcessingCloud
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.color_lens_outlined, color: Colors.white, size: 18),
                                SizedBox(width: 8),
                                Text(
                                  'Colorize (Grayscale)',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 13,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: GestureDetector(
                  onTap: _isProcessingCloud ? null : () => _processCloudImage('resolution'),
                  child: Container(
                    height: 40,
                    decoration: BoxDecoration(
                      color: const Color(0xFF1C1310),
                      borderRadius: BorderRadius.circular(12.0),
                      border: Border.all(color: const Color(0xFFD46A36).withOpacity(0.5)),
                    ),
                    child: const Center(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.aspect_ratio, color: Color(0xFFD46A36), size: 18),
                          SizedBox(width: 8),
                          Text(
                            'Get Resolution',
                            style: TextStyle(
                              color: Color(0xFFD46A36),
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildChatStudioSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.25),
        borderRadius: BorderRadius.circular(24.0),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Text(
              'Chat Studio',
              style: GoogleFonts.playfairDisplay(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 12.0),
          
          // Chat Output Box
          Container(
            height: 200,
            width: double.infinity,
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: const Color(0xFF1C1310).withOpacity(0.7),
              borderRadius: BorderRadius.circular(16.0),
              border: Border.all(color: const Color(0xFFD46A36).withOpacity(0.2)),
            ),
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    controller: _chatScrollController,
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final msg = _messages[index];
                      final sender = msg['sender'] ?? '';
                      final text = msg['text'] ?? '';
                      final isBot = sender == 'MUNCH';
                      final isSystem = sender == 'SYSTEM';

                      Color nameColor = const Color(0xFFD46A36);
                      if (isBot) nameColor = Colors.white;
                      if (isSystem) nameColor = Colors.redAccent;

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 10.0),
                        child: RichText(
                          text: TextSpan(
                            style: const TextStyle(color: Color(0xFFE0E0E0), fontSize: 14),
                            children: [
                              TextSpan(
                                text: '$sender: ',
                                style: TextStyle(
                                  color: nameColor,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                  letterSpacing: 0.5,
                                ),
                              ),
                              TextSpan(text: text),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                if (_isSendingMessage)
                  Padding(
                    padding: const EdgeInsets.only(top: 4.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: [
                        const SizedBox(
                          width: 12,
                          height: 12,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFD46A36)),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Munch is thinking...',
                          style: TextStyle(color: Colors.grey[500], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 12.0),
          
          // Chat Input Group
          Row(
            children: [
              // Voice Button
              GestureDetector(
                onTap: _toggleListening,
                child: Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: _isListening 
                        ? const Color(0xFFD46A36) 
                        : const Color(0xFFD46A36).withOpacity(0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFFD46A36), width: 1.5),
                  ),
                  child: Center(
                    child: Image.asset(
                      'assets/images/Mic.png',
                      width: 20,
                      height: 20,
                      color: _isListening ? Colors.white : const Color(0xFFD46A36),
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(
                          _isListening ? Icons.mic : Icons.mic_none_outlined,
                          color: _isListening ? Colors.white : const Color(0xFFD46A36),
                          size: 20,
                        );
                      },
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              
              // Text Field and Send Button
              Expanded(
                child: Container(
                  height: 44,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1C1310).withOpacity(0.8),
                    borderRadius: BorderRadius.circular(22.0),
                    border: Border.all(color: const Color(0xFFD46A36).withOpacity(0.2)),
                  ),
                  padding: const EdgeInsets.only(left: 16.0, right: 6.0),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _chatInputController,
                          style: const TextStyle(fontSize: 14, color: Colors.white),
                          decoration: InputDecoration(
                            hintText: _isListening ? 'Listening...' : 'Type your message here.',
                            hintStyle: TextStyle(
                              color: _isListening ? const Color(0xFFD46A36) : Colors.grey[600],
                              fontStyle: FontStyle.italic,
                            ),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.zero,
                          ),
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                      GestureDetector(
                        onTap: _isSendingMessage ? null : _sendMessage,
                        child: Container(
                          width: 34,
                          height: 34,
                          decoration: const BoxDecoration(
                            color: Colors.transparent,
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Image.asset(
                              'assets/images/Send.png',
                              width: 16,
                              height: 16,
                              color: const Color(0xFFD46A36),
                              errorBuilder: (context, error, stackTrace) {
                                return const Icon(Icons.send, color: Color(0xFFD46A36), size: 16);
                              },
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
