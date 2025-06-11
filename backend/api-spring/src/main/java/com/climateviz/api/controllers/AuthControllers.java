package com.climateviz.api.controllers;

import com.climateviz.api.persistence.entity.UserEntity;
import com.climateviz.api.persistence.repository.UserRepository;
import com.climateviz.api.services.interfaces.IAuthService;
import com.climateviz.api.models.dto.LoginDTO;
import com.climateviz.api.models.dto.ResponseDTO;
import com.climateviz.api.models.dto.ForgotPasswordDTO;
import com.climateviz.api.models.dto.ResetPasswordDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.HashMap;
import java.util.Optional;

@RestController
@RequestMapping("/auth")
public class AuthControllers {

    @Autowired
    IAuthService authService;
    
    @Autowired
    private UserRepository userRepository;

    @PostMapping("/register")
    private ResponseEntity<ResponseDTO> register(@RequestBody UserEntity user) throws Exception {
        return new ResponseEntity<>(authService.register(user), HttpStatus.CREATED);
    }

    @PostMapping("/login")
    private ResponseEntity<HashMap<String, String>> login(@RequestBody LoginDTO loginRequest) throws Exception {
        HashMap<String, String> login = authService.login(loginRequest);

        if (login.containsKey("jwt")) {
            return new ResponseEntity<>(login, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(login, HttpStatus.UNAUTHORIZED);
        }
    }

    @GetMapping("/verify")
    public ResponseEntity<HashMap<String, String>> verifyUser(@RequestParam("code") String code) throws Exception {
        HashMap<String, String> response = authService.verifyUser(code);
        
        if (response.containsKey("success")) {
            return new ResponseEntity<>(response, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<HashMap<String, String>> forgotPassword(@RequestBody ForgotPasswordDTO request) throws Exception {
        HashMap<String, String> response = authService.forgotPassword(request.getEmail());
        
        if (response.containsKey("success")) {
            return new ResponseEntity<>(response, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
    }

    @PostMapping("/reset-password")
    public ResponseEntity<HashMap<String, String>> resetPassword(@RequestBody ResetPasswordDTO request) throws Exception {
        HashMap<String, String> response = authService.resetPassword(request.getToken(), request.getNewPassword());
        
        if (response.containsKey("success")) {
            return new ResponseEntity<>(response, HttpStatus.OK);
        } else {
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
    }

    @GetMapping("/reset-password")
    public ResponseEntity<HashMap<String, String>> validateResetToken(@RequestParam("token") String token) throws Exception {
        HashMap<String, String> response = new HashMap<>();
        
        Optional<UserEntity> userOptional = userRepository.findByPasswordResetToken(token);
        
        if (userOptional.isEmpty()) {
            response.put("error", "Invalid reset token");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
        
        UserEntity user = userOptional.get();
        if (isTokenExpired(user.getTokenCreationDate())) {
            response.put("error", "Reset token has expired");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
        
        response.put("success", "Valid token");
        response.put("email", user.getEmail());
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    // Método helper para validar token
    private boolean isTokenExpired(LocalDateTime tokenCreationDate) {
        if (tokenCreationDate == null) {
            return true;
        }
        LocalDateTime now = LocalDateTime.now();
        Duration diff = Duration.between(tokenCreationDate, now);
        return diff.toHours() >= 24;
    }
}
