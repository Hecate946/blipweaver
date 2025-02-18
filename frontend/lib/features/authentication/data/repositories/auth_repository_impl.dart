import 'package:frontend/features/authentication/data/datasources/auth_remote_data_source.dart';
import 'package:frontend/features/authentication/domain/entities/user.dart';
import 'package:frontend/features/authentication/domain/repositories/auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource remoteDataSource;

  AuthRepositoryImpl({required this.remoteDataSource});

  @override
  Future<User> login(String identifier, String password) async {
    return await remoteDataSource.login(identifier, password);
  }

  @override
  Future<void> signup(String username, String email, String password) async {
    await remoteDataSource.signup(username, email, password);
  }
}
