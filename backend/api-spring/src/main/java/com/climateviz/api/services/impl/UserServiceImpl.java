package com.climateviz.api.services.impl;

import com.climateviz.api.persistence.entity.UserEntity;
import com.climateviz.api.persistence.repository.UserRepository;
import com.climateviz.api.services.interfaces.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class UserServiceImpl implements IUserService {
    @Autowired
    UserRepository userRepository;

    @Override
    public List<UserEntity> findAllUsers() {
        return userRepository.findAll();
    }

    @Override
    public UserEntity findUserById(Long id) {
        Optional<UserEntity> userOpt = userRepository.findById(id);
        return userOpt.orElse(null);
    }

    @Override
    public UserEntity updateUser(Long id, UserEntity updatedUser) {
        Optional<UserEntity> userOpt = userRepository.findById(id);
        if (userOpt.isPresent()) {
            UserEntity user = userOpt.get();
            user.setUsername(updatedUser.getUsername());
            user.setEmail(updatedUser.getEmail());
            return userRepository.save(user);
        } else {
            return null;
        }
    }

    @Override
    public boolean deleteUser(Long id) {
        if (userRepository.existsById(id)) {
            userRepository.deleteById(id);
            return true;
        } else {
            return false;
        }
    }
}
