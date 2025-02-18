import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/authentication/presentation/pages/login_screen.dart';
import 'package:frontend/injection_container.dart'; // Ensure providers are registered

void main() {
  runApp(ProviderScope(child: MyApp())); // ✅ Ensures Riverpod is initialized
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'BlipWeaver',
      home: LoginScreen(),
    );
  }
}
