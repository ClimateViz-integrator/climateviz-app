package com.climateviz.api.controllers;

import com.climateviz.api.persistence.entities.UserEntity;
import com.climateviz.api.services.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/user")
public class UserControllers {

    @Autowired
    IUserService userService;

    @GetMapping("/find-all")
    private ResponseEntity<List<UserEntity>> getAllUsers() {
        return new ResponseEntity<>(userService.findAllUsers(), HttpStatus.OK);
    }
}
