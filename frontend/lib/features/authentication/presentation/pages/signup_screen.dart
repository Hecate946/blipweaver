import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/authentication/presentation/providers/signup_provider.dart';

class SignupScreen extends ConsumerWidget {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final signup = ref.watch(signupProvider);

    return Scaffold(
      appBar: AppBar(title: Text('Signup for BlipWeaver')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: usernameController,
              decoration: InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: emailController,
              decoration: InputDecoration(labelText: 'Email'),
            ),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: InputDecoration(labelText: 'Password'),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                bool success = await ref.read(signupProvider.notifier).signup(
                  usernameController.text,
                  emailController.text,
                  passwordController.text
                );
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Signup Successful!'))
                  );
                  Navigator.pop(context);  // Redirect back to login
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Signup Failed!'))
                  );
                }
              },
              child: signup ? CircularProgressIndicator() : Text('Signup'),
            ),
          ],
        ),
      ),
    );
  }
}
