package com.climateviz.api.services.implementation;

import com.climateviz.api.persistence.entities.UserEntity;
import com.climateviz.api.persistence.repositories.UserRepository;
import com.climateviz.api.services.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserServiceImplementation implements IUserService {
    @Autowired
    UserRepository userRepository;

    @Override
    public List<UserEntity> findAllUsers() {
        return userRepository.findAll();
    }
}
