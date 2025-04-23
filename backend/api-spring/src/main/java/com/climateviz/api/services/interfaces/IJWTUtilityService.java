package com.climateviz.api.services.interfaces;

import com.nimbusds.jose.JOSEException;
import com.nimbusds.jwt.JWTClaimsSet;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.security.spec.InvalidKeySpecException;
import java.text.ParseException;

public interface IJWTUtilityService {
    public String generateJWT(Long userId)
            throws IOException, NoSuchAlgorithmException, InvalidKeySpecException, JOSEException;

    public JWTClaimsSet parseJWT(String jwt)
            throws NoSuchAlgorithmException, IOException, InvalidKeySpecException, ParseException, JOSEException;
}
