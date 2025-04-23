package com.climateviz.api.services.interfaces;

import com.climateviz.api.persistence.entity.UserEntity;

import java.util.List;

public interface IUserService {
    public List<UserEntity> findAllUsers();
    public UserEntity findUserById(Long id);
    public UserEntity updateUser(Long id, UserEntity updatedUser);
    public boolean deleteUser(Long id);
}
