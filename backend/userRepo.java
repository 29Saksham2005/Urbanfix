package com.UF.Urbanfix;

import org.springframework.data.jpa.repository.JpaRepository;
import com.smartcomplaint.model.User;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}