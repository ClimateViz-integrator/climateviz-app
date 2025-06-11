package com.climateviz.api.services.impl;

import com.climateviz.api.persistence.entity.UserEntity;
import com.climateviz.api.persistence.repository.UserRepository;
import com.climateviz.api.services.interfaces.IAuthService;
import com.climateviz.api.services.interfaces.IJWTUtilityService;
import com.climateviz.api.models.dto.LoginDTO;
import com.climateviz.api.models.dto.ResponseDTO;
import com.climateviz.api.models.validation.UserValidation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;
import java.io.UnsupportedEncodingException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class AuthServiceImplementation implements IAuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private IJWTUtilityService jwtUtilityService;

    @Autowired
    private UserValidation userValidation;

    @Autowired
    private JavaMailSender mailSender;

    @Value("${app.base-url}")
    private String baseUrl;

    @Value("${spring.mail.username}")
    private String fromAddress;

    @Override
    public HashMap<String, String> login(LoginDTO login) throws Exception {
        try {
            HashMap<String, String> jwt = new HashMap<>();
            Optional<UserEntity> user = userRepository.findByEmail(login.getEmail());

            // Verificar el email
            if (user.isEmpty()) {
                jwt.put("error", "User not registered!");
                return jwt;
            }

            // Verificar si la cuenta está habilitada
            if (!user.get().isEnabled()) {
                jwt.put("error", "Account not verified. Please check your email.");
                return jwt;
            }

            // Verificar la contraseña
            if (verifyPassword(login.getPassword(), user.get().getPassword())) {
                jwt.put("jwt", jwtUtilityService.generateJWT(user.get().getId()));
            } else {
                jwt.put("error", "Authentication failed");
            }
            return jwt;
        } catch (Exception e) {
            throw new Exception(e.toString());
        }
    }

    @Override
    public ResponseDTO register(UserEntity user) throws Exception {
        try {
            ResponseDTO response = userValidation.validate(user);

            if (response.getNumOfErrors() > 0) {
                return response;
            }

            List<UserEntity> getAllUsers = userRepository.findAll();

            for (UserEntity repetFields : getAllUsers) {
                if (repetFields.getEmail().equals(user.getEmail())) {
                    response.setNumOfErrors(1);
                    response.setMessage("User already exists!");
                    return response;
                }
            }

            String verificationCode = UUID.randomUUID().toString().replace("-", "");
            user.setVerificationCode(verificationCode);
            user.setEnabled(false);

            BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
            user.setPassword(encoder.encode(user.getPassword()));
            userRepository.save(user);

            // Enviar correo de verificación
            try {
                sendVerificationEmail(user);
                response.setMessage("User created successfully. Please check your email to verify your account.");
            } catch (Exception e) {
                response.setMessage("User created but failed to send verification email. Please contact support.");
            }

            return response;
        } catch (Exception e) {
            throw new Exception(e.toString());
        }
    }

    @Override
    public HashMap<String, String> verifyUser(String verificationCode) throws Exception {
        HashMap<String, String> response = new HashMap<>();

        try {
            Optional<UserEntity> userOptional = userRepository.findByVerificationCode(verificationCode);

            if (userOptional.isEmpty()) {
                response.put("error", "Invalid verification code");
                return response;
            }

            UserEntity user = userOptional.get();

            if (user.isEnabled()) {
                response.put("error", "Account already verified");
                return response;
            }

            // Activar la cuenta
            user.setEnabled(true);
            user.setVerificationCode(null);
            userRepository.save(user);

            response.put("success", "Account verified successfully");
            return response;

        } catch (Exception e) {
            throw new Exception("Error during verification: " + e.getMessage());
        }
    }

    private void sendVerificationEmail(UserEntity user) throws MessagingException, UnsupportedEncodingException {
        String toAddress = user.getEmail();
        String senderName = "ClimateViz";
        String subject = "Verifica tu cuenta - ClimateViz";

        String content = "<!DOCTYPE html>"
                + "<html>"
                + "<head>"
                + "<style>"
                + "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }"
                + ".container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }"
                + ".header { text-align: center; color: #333; }"
                + ".button { display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }"
                + ".footer { color: #666; font-size: 12px; text-align: center; margin-top: 20px; }"
                + "</style>"
                + "</head>"
                + "<body>"
                + "<div class='container'>"
                + "<h2 class='header'>¡Bienvenido a ClimateViz!</h2>"
                + "<p>Hola <strong>[[name]]</strong>,</p>"
                + "<p>Gracias por registrarte en ClimateViz. Para completar tu registro, necesitas verificar tu dirección de correo electrónico.</p>"
                + "<p>Haz clic en el siguiente botón para verificar tu cuenta:</p>"
                + "<div style='text-align: center;'>"
                + "<a href='[[URL]]' class='button'>VERIFICAR CUENTA</a>"
                + "</div>"
                + "<p>Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:</p>"
                + "<p><a href='[[URL]]'>[[URL]]</a></p>"
                + "<p>Si no te registraste en ClimateViz, puedes ignorar este correo.</p>"
                + "<div class='footer'>"
                + "<p>Este es un correo automático, por favor no respondas a este mensaje.</p>"
                + "<p>&copy; 2025 ClimateViz. Todos los derechos reservados.</p>"
                + "</div>"
                + "</div>"
                + "</body>"
                + "</html>";

        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message);

        helper.setFrom(fromAddress, senderName);
        helper.setTo(toAddress);
        helper.setSubject(subject);

        content = content.replace("[[name]]", user.getUsername());
        String verifyURL = baseUrl + "/auth/verify?code=" + user.getVerificationCode();
        content = content.replace("[[URL]]", verifyURL);

        helper.setText(content, true);
        mailSender.send(message);
    }

    private boolean verifyPassword(String enteredPassword, String storedPassword) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        return encoder.matches(enteredPassword, storedPassword);
    }

    @Override
    public HashMap<String, String> forgotPassword(String email) throws Exception {
        HashMap<String, String> response = new HashMap<>();

        try {
            Optional<UserEntity> userOptional = userRepository.findByEmail(email);

            if (userOptional.isEmpty()) {
                response.put("error", "No account found with this email address");
                return response;
            }

            UserEntity user = userOptional.get();

            if (!user.isEnabled()) {
                response.put("error", "Account not verified. Please verify your account first");
                return response;
            }

            // Generar token de reset
            String resetToken = UUID.randomUUID().toString().replace("-", "");
            user.setPasswordResetToken(resetToken);
            user.setTokenCreationDate(LocalDateTime.now());
            userRepository.save(user);

            // Enviar correo de reset
            try {
                sendPasswordResetEmail(user);
                response.put("success", "Password reset email sent successfully");
            } catch (Exception e) {
                response.put("error", "Failed to send password reset email");
            }

            return response;

        } catch (Exception e) {
            throw new Exception("Error processing forgot password request: " + e.getMessage());
        }
    }

    @Override
    public HashMap<String, String> resetPassword(String token, String newPassword) throws Exception {
        HashMap<String, String> response = new HashMap<>();

        try {
            Optional<UserEntity> userOptional = userRepository.findByPasswordResetToken(token);

            if (userOptional.isEmpty()) {
                response.put("error", "Invalid reset token");
                return response;
            }

            UserEntity user = userOptional.get();

            // Verificar si el token ha expirado (24 horas)
            if (isTokenExpired(user.getTokenCreationDate())) {
                response.put("error", "Reset token has expired");
                return response;
            }

            // Actualizar contraseña
            BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
            user.setPassword(encoder.encode(newPassword));
            user.setPasswordResetToken(null);
            user.setTokenCreationDate(null);
            userRepository.save(user);

            response.put("success", "Password updated successfully");
            return response;

        } catch (Exception e) {
            throw new Exception("Error resetting password: " + e.getMessage());
        }
    }

    private void sendPasswordResetEmail(UserEntity user) throws MessagingException, UnsupportedEncodingException {
        String toAddress = user.getEmail();
        String senderName = "ClimateViz";
        String subject = "Restablecer contraseña - ClimateViz";

        String content = "<!DOCTYPE html>"
                + "<html>"
                + "<head>"
                + "<style>"
                + "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }"
                + ".container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }"
                + ".header { text-align: center; color: #333; }"
                + ".button { display: inline-block; padding: 12px 24px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }"
                + ".footer { color: #666; font-size: 12px; text-align: center; margin-top: 20px; }"
                + "</style>"
                + "</head>"
                + "<body>"
                + "<div class='container'>"
                + "<h2 class='header'>Restablecer Contraseña</h2>"
                + "<p>Hola <strong>[[name]]</strong>,</p>"
                + "<p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en ClimateViz.</p>"
                + "<p>Haz clic en el siguiente botón para restablecer tu contraseña:</p>"
                + "<div style='text-align: center;'>"
                + "<a href='[[URL]]' class='button'>RESTABLECER CONTRASEÑA</a>"
                + "</div>"
                + "<p>Si no puedes hacer clic en el botón, copia y pega el siguiente enlace en tu navegador:</p>"
                + "<p><a href='[[URL]]'>[[URL]]</a></p>"
                + "<p><strong>Este enlace expirará en 24 horas.</strong></p>"
                + "<p>Si no solicitaste este cambio, puedes ignorar este correo.</p>"
                + "<div class='footer'>"
                + "<p>Este es un correo automático, por favor no respondas a este mensaje.</p>"
                + "<p>&copy; 2025 ClimateViz. Todos los derechos reservados.</p>"
                + "</div>"
                + "</div>"
                + "</body>"
                + "</html>";

        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message);

        helper.setFrom(fromAddress, senderName);
        helper.setTo(toAddress);
        helper.setSubject(subject);

        content = content.replace("[[name]]", user.getUsername());
        String resetURL = baseUrl + "/reset-password?code=" + user.getPasswordResetToken();
        content = content.replace("[[URL]]", resetURL);

        helper.setText(content, true);
        mailSender.send(message);
    }

    private boolean isTokenExpired(LocalDateTime tokenCreationDate) {
        LocalDateTime now = LocalDateTime.now();
        Duration diff = Duration.between(tokenCreationDate, now);
        return diff.toHours() >= 24; // Token expira en 24 horas
    }

}
