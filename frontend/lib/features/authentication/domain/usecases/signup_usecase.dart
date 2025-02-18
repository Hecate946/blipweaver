import 'package:frontend/features/authentication/domain/repositories/auth_repository.dart';

class SignupUseCase {
  final AuthRepository repository;

  SignupUseCase({required this.repository});

  Future<void> call(String username, String email, String password) async {
    await repository.signup(username, email, password);
  }
}
