import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/authentication/domain/usecases/signup_usecase.dart';
import 'package:frontend/injection_container.dart';

final signupProvider = StateNotifierProvider<SignupNotifier, bool>((ref) {
  final signupUseCase = ref.watch(signupUseCaseProvider); // ✅ Ensure provider is registered
  return SignupNotifier(signupUseCase);
});

class SignupNotifier extends StateNotifier<bool> {
  final SignupUseCase signupUseCase;

  SignupNotifier(this.signupUseCase) : super(false);

  Future<bool> signup(String username, String email, String password) async {
    try {
      await signupUseCase(username, email, password);
      state = true;
      return true;
    } catch (e) {
      return false;
    }
  }
}
