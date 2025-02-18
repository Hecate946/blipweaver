import 'package:frontend/features/authentication/domain/entities/user.dart';

abstract class AuthRepository {
  Future<User> login(String identifier, String password);
  Future<void> signup(String username, String email, String password); // ✅ Add this line
}
