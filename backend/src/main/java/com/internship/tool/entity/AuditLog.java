package com.internship.tool.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "audit_logs")
public class AuditLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String entityName;
    private UUID entityId;
    private String action;
    private String changedBy;
    private OffsetDateTime changeTime;
    private String details;

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getEntityName() { return entityName; }
    public void setEntityName(String entityName) { this.entityName = entityName; }
    public UUID getEntityId() { return entityId; }
    public void setEntityId(UUID entityId) { this.entityId = entityId; }
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }
    public String getChangedBy() { return changedBy; }
    public void setChangedBy(String changedBy) { this.changedBy = changedBy; }
    public OffsetDateTime getChangeTime() { return changeTime; }
    public void setChangeTime(OffsetDateTime changeTime) { this.changeTime = changeTime; }
    public String getDetails() { return details; }
    public void setDetails(String details) { this.details = details; }
}
