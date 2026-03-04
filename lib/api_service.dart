import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

class ApiService {
  // If using Android Emulator, use 10.0.2.2.
  // If using a real device, use your laptop's IP (e.g., 192.168.1.XX)
  static const String _baseUrl = 'http://10.0.2.2:8000';

  Future<String> getNovaResponse(String prompt, XFile? image) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$_baseUrl/ask-nova'));
      request.fields['prompt'] = prompt;

      if (image != null) {
        request.files.add(await http.MultipartFile.fromPath('image', image.path));
      }

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return json.decode(response.body)['response'];
      } else {
        return "Server Error: ${response.statusCode}";
      }
    } catch (e) {
      return "Check if your Python backend is running! Error: $e";
    }
  }
}