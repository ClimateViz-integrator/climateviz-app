package com.climateviz.api.services.interfaces;

import com.climateviz.api.persistence.entity.UserEntity;
import com.climateviz.api.models.dto.LoginDTO;
import com.climateviz.api.models.dto.ResponseDTO;

import java.util.HashMap;

public interface IAuthService {

    public HashMap<String, String> login(LoginDTO login) throws Exception;

    public ResponseDTO register(UserEntity user) throws Exception;

    HashMap<String, String> verifyUser(String verificationCode) throws Exception;
}
