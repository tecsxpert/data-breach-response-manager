package com.internship.tool.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.UUID;
import com.internship.tool.entity.AuditLog; // Assuming this will be created by Java Dev 1

@Repository
public interface AuditLogRepository extends JpaRepository<AuditLog, Long> {
}
