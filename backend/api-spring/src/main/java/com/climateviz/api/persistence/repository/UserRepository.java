package com.climateviz.api.persistence.repository;


import com.climateviz.api.persistence.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface UserRepository extends JpaRepository<UserEntity, Long> {
    @Query(value = "SELECT * FROM user WHERE email = :email", nativeQuery = true)
    Optional<UserEntity> findByEmail(String email);

    Optional<UserEntity> findByVerificationCode(String verificationCode);

    // Method to find a user by password reset token
    Optional<UserEntity> findByPasswordResetToken(String token);

}
