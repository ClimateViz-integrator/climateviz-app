package com.climateviz.api.services;

import com.climateviz.api.persistence.entities.UserEntity;
import com.climateviz.api.services.models.dtos.LoginDTO;
import com.climateviz.api.services.models.dtos.ResponseDTO;

import java.util.HashMap;

public interface IAuthService {

    public HashMap<String, String> login(LoginDTO login) throws Exception;

    public ResponseDTO register(UserEntity user) throws Exception;
}
