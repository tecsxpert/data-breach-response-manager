package com.internship.tool.aspect;

import com.internship.tool.entity.AuditLog;
import com.internship.tool.repository.AuditLogRepository;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.AfterReturning;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.UUID;

@Aspect
@Component
public class AuditAspect {

    @Autowired
    private AuditLogRepository auditLogRepository;

    // Pointcut that matches all repository save/delete methods in the com.internship.tool package
    @Pointcut("execution(* com.internship.tool.repository.*.save*(..)) || execution(* com.internship.tool.repository.*.delete*(..))")
    public void cudMethods() {}

    @AfterReturning(pointcut = "cudMethods()", returning = "result")
    public void logAfterReturning(JoinPoint joinPoint, Object result) {
        String methodName = joinPoint.getSignature().getName();
        String action = methodName.startsWith("save") ? "CREATE/UPDATE" : "DELETE";
        
        Object entity = result;
        if (entity == null && joinPoint.getArgs().length > 0) {
            entity = joinPoint.getArgs()[0];
        }

        if (entity != null) {
            AuditLog log = new AuditLog();
            log.setEntityName(entity.getClass().getSimpleName());
            log.setAction(action);
            log.setChangedBy("system"); // Could be replaced with actual user from SecurityContextHolder
            log.setChangeTime(OffsetDateTime.now());
            
            // Just a basic generic way to try to get ID. In real world, use Reflection or an interface like Identifiable.
            try {
                java.lang.reflect.Method getIdMethod = entity.getClass().getMethod("getId");
                Object idObj = getIdMethod.invoke(entity);
                if (idObj instanceof UUID) {
                    log.setEntityId((UUID) idObj);
                }
            } catch (Exception e) {
                // Ignore if no getId method or ID is not UUID
            }
            
            log.setDetails("Method " + methodName + " called on " + entity.getClass().getSimpleName());
            
            // Only log if it's an entity we care about, not the AuditLog itself to prevent recursion
            if (!log.getEntityName().equals("AuditLog")) {
                auditLogRepository.save(log);
            }
        }
    }
}
