import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/authentication/domain/usecases/login_usecase.dart';
import 'package:frontend/injection_container.dart';

final authProvider = StateNotifierProvider<AuthNotifier, bool>((ref) {
  final loginUseCase = ref.watch(loginUseCaseProvider); // ✅ Ensure correct provider access
  return AuthNotifier(loginUseCase);
});

class AuthNotifier extends StateNotifier<bool> {
  final LoginUseCase loginUseCase;

  AuthNotifier(this.loginUseCase) : super(false);

  Future<bool> login(String identifier, String password) async {
    try {
      await loginUseCase(identifier, password);
      state = true;
      return true;
    } catch (e) {
      return false;
    }
  }
}
