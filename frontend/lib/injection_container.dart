import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:frontend/features/authentication/data/datasources/auth_remote_data_source.dart';
import 'package:frontend/features/authentication/data/repositories/auth_repository_impl.dart';
import 'package:frontend/features/authentication/domain/repositories/auth_repository.dart';
import 'package:frontend/features/authentication/domain/usecases/login_usecase.dart';
import 'package:frontend/features/authentication/domain/usecases/signup_usecase.dart';

// Dio HTTP Client
final dioProvider = Provider((ref) => Dio());

// Data Source Provider
final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  return AuthRemoteDataSourceImpl(dio: ref.read(dioProvider));
});

// Repository Provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(remoteDataSource: ref.read(authRemoteDataSourceProvider));
});

// ✅ Login Use Case Provider
final loginUseCaseProvider = Provider<LoginUseCase>((ref) {
  return LoginUseCase(repository: ref.read(authRepositoryProvider));
});

// ✅ Signup Use Case Provider
final signupUseCaseProvider = Provider<SignupUseCase>((ref) {
  return SignupUseCase(repository: ref.read(authRepositoryProvider));
});
