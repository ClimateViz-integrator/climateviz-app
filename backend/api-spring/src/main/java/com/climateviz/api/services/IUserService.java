package com.climateviz.api.services;

import com.climateviz.api.persistence.entities.UserEntity;

import java.util.List;

public interface IUserService {
    public List<UserEntity> findAllUsers();
}
