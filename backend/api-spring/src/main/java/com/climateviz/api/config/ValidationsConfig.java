package com.climateviz.api.config;

import com.climateviz.api.models.validation.UserValidation;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class ValidationsConfig {
    @Bean
    public UserValidation userValidation(){
        return new UserValidation();
    }
}
