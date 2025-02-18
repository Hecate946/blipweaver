import 'package:frontend/features/authentication/domain/entities/user.dart';

class LoginModel extends User {
  LoginModel({required String email, required String username})
      : super(email: email, username: username);

  factory LoginModel.fromJson(Map<String, dynamic> json) {
    return LoginModel(
      email: json['email'],
      username: json['username'],
    );
  }
}
