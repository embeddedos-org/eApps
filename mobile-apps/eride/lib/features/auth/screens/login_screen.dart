import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/validators.dart';
import '../../../core/providers/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              _buildHeader(),
              const SizedBox(height: 40),
              _buildForm(),
              const SizedBox(height: 16),
              if (_errorMessage != null) _buildErrorBanner(),
              const SizedBox(height: 24),
              _buildLoginButton(),
              const SizedBox(height: 16),
              _buildForgotPassword(),
              const SizedBox(height: 32),
              _buildDivider(),
              const SizedBox(height: 24),
              _buildSocialButtons(),
              const SizedBox(height: 32),
              _buildRegisterLink(),
              const SizedBox(height: 16),
              _buildSkipButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(children: [
      Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.primaryContainer, shape: BoxShape.circle,
        ),
        child: const Icon(Icons.directions_car, size: 48, color: AppColors.primary),
      ),
      const SizedBox(height: 20),
      const Text('Welcome to eRide',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
      const SizedBox(height: 8),
      const Text('Sign in to continue your journey',
          style: TextStyle(fontSize: 15, color: AppColors.textSecondary)),
    ]);
  }

  Widget _buildForm() {
    return Form(
      key: _formKey,
      child: Column(children: [
        TextFormField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          textInputAction: TextInputAction.next,
          validator: Validators.validateEmail,
          decoration: const InputDecoration(
            labelText: 'Email', hintText: 'you@example.com',
            prefixIcon: Icon(Icons.email_outlined),
          ),
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          textInputAction: TextInputAction.done,
          validator: Validators.validatePassword,
          onFieldSubmitted: (_) => _handleLogin(),
          decoration: InputDecoration(
            labelText: 'Password', hintText: 'Enter your password',
            prefixIcon: const Icon(Icons.lock_outlined),
            suffixIcon: IconButton(
              icon: Icon(_obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
            ),
          ),
        ),
      ]),
    );
  }

  Widget _buildErrorBanner() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.errorLight, borderRadius: BorderRadius.circular(10),
      ),
      child: Row(children: [
        const Icon(Icons.error_outline, color: AppColors.error, size: 20),
        const SizedBox(width: 10),
        Expanded(child: Text(_errorMessage!,
            style: const TextStyle(color: AppColors.error, fontSize: 13))),
        IconButton(icon: const Icon(Icons.close, size: 16, color: AppColors.error),
            onPressed: () => setState(() => _errorMessage = null)),
      ]),
    );
  }

  Widget _buildLoginButton() {
    return SizedBox(
      height: 52,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _handleLogin,
        child: _isLoading
            ? const SizedBox(width: 22, height: 22,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : const Text('Sign In', style: TextStyle(fontSize: 16)),
      ),
    );
  }

  Widget _buildForgotPassword() {
    return Center(
      child: TextButton(
        onPressed: () => _showForgotPasswordDialog(),
        child: const Text('Forgot Password?'),
      ),
    );
  }

  Widget _buildDivider() {
    return const Row(children: [
      Expanded(child: Divider()),
      Padding(padding: EdgeInsets.symmetric(horizontal: 16),
          child: Text('or continue with', style: TextStyle(color: AppColors.textSecondary, fontSize: 13))),
      Expanded(child: Divider()),
    ]);
  }

  Widget _buildSocialButtons() {
    return Row(children: [
      Expanded(child: OutlinedButton.icon(
        onPressed: () => _handleSocialLogin('Google'),
        icon: const Icon(Icons.g_mobiledata, size: 24),
        label: const Text('Google'),
        style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
      )),
      const SizedBox(width: 12),
      Expanded(child: OutlinedButton.icon(
        onPressed: () => _handleSocialLogin('Apple'),
        icon: const Icon(Icons.apple, size: 22),
        label: const Text('Apple'),
        style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
      )),
    ]);
  }

  Widget _buildRegisterLink() {
    return Row(mainAxisAlignment: MainAxisAlignment.center, children: [
      const Text("Don't have an account?", style: TextStyle(color: AppColors.textSecondary)),
      TextButton(
        onPressed: () => context.push(AppConstants.registerRoute),
        child: const Text('Sign Up', style: TextStyle(fontWeight: FontWeight.w600)),
      ),
    ]);
  }

  Widget _buildSkipButton() {
    return Center(child: TextButton(
      onPressed: () => context.go(AppConstants.homeRoute),
      child: const Text('Skip for now', style: TextStyle(color: AppColors.textSecondary)),
    ));
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _isLoading = true; _errorMessage = null; });
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) {
      setState(() => _isLoading = false);
      context.go(AppConstants.homeRoute);
    }
  }

  void _handleSocialLogin(String provider) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('$provider sign-in coming soon'), behavior: SnackBarBehavior.floating),
    );
  }

  void _showForgotPasswordDialog() {
    final controller = TextEditingController();
    showDialog(context: context, builder: (ctx) => AlertDialog(
      title: const Text('Reset Password'),
      content: Column(mainAxisSize: MainAxisSize.min, children: [
        const Text('Enter your email to receive a password reset link.',
            style: TextStyle(color: AppColors.textSecondary, fontSize: 14)),
        const SizedBox(height: 16),
        TextField(controller: controller,
            decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined)),
            keyboardType: TextInputType.emailAddress),
      ]),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
        ElevatedButton(onPressed: () {
          Navigator.pop(ctx);
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Password reset email sent!'), backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating));
        }, child: const Text('Send')),
      ],
    ));
  }
}
