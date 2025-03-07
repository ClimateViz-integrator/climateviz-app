package com.climateviz.api.services.implementation;

import com.climateviz.api.persistence.entities.UserEntity;
import com.climateviz.api.persistence.repositories.UserRepository;
import com.climateviz.api.services.IAuthService;
import com.climateviz.api.services.IJWTUtilityService;
import com.climateviz.api.services.models.dtos.LoginDTO;
import com.climateviz.api.services.models.dtos.ResponseDTO;
import com.climateviz.api.services.models.validation.UserValidation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Optional;

@Service
public class AuthServiceImplementation implements IAuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private IJWTUtilityService jwtUtilityService;

    @Autowired
    private UserValidation userValidation;

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

            /*
            for (UserEntity repetFields : getAllUsers) {
                if (repetFields != null) {
                    response.setNumOfErrors(1);
                    response.setMessage("User already exists!");
                    return response;
                }
            }
            */

            for (UserEntity repetFields : getAllUsers) {
                if (repetFields.getEmail().equals(user.getEmail())) {
                    response.setNumOfErrors(1);
                    response.setMessage("User already exists!");
                    return response;
                }
            }

            BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
            user.setPassword(encoder.encode(user.getPassword()));
            userRepository.save(user);
            response.setMessage("User created succesfully");

            return response;
        } catch (Exception e) {
            throw new Exception(e.toString());
        }
    }

    private boolean verifyPassword(String enteredPassword, String storedPassword) {
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

        //Si hacer mach nos regresa true y si no false
        return encoder.matches(enteredPassword, storedPassword);
    }
}
