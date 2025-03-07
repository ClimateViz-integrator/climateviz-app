package com.climateviz.api.persistence.repositories;


import com.climateviz.api.persistence.entities.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface UserRepository extends JpaRepository<UserEntity, Long> {
    @Query(value = "SELECT * FROM user WHERE email = :email", nativeQuery = true)
    Optional<UserEntity> findByEmail(String email);
}
