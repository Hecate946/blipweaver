import 'package:dio/dio.dart';
import 'package:frontend/core/constants.dart';
import 'package:frontend/features/authentication/data/models/login_model.dart';

abstract class AuthRemoteDataSource {
  Future<LoginModel> login(String identifier, String password);
  Future<void> signup(String username, String email, String password); // ✅ No need for separate API service
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final Dio dio;

  AuthRemoteDataSourceImpl({required this.dio});

  @override
  Future<LoginModel> login(String identifier, String password) async {
    try {
      final response = await dio.post('${Constants.baseUrl}/login', data: {
        "identifier": identifier,
        "password": password
      });
      return LoginModel.fromJson(response.data);
    } catch (e) {
      print("Login API Error: $e"); // ✅ Log errors instead of crashing
      throw Exception("Login failed");
    }
  }

  @override
  Future<void> signup(String username, String email, String password) async {
    try {
      await dio.post('${Constants.baseUrl}/signup', data: {
        "username": username,
        "email": email,
        "password": password
      });
    } catch (e) {
      print("Signup API Error: $e"); // ✅ Log errors for debugging
      throw Exception("Signup failed");
    }
  }
}
