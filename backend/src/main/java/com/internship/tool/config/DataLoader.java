package com.internship.tool.config;

import com.internship.tool.entity.DataBreach;
import com.internship.tool.repository.DataBreachRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.List;

@Component
public class DataLoader implements CommandLineRunner {

    @Autowired
    private DataBreachRepository repository;

    @Override
    public void run(String... args) throws Exception {
        if (repository.count() == 0) {
            List<DataBreach> seedData = Arrays.asList(
                createBreach("Customer Database Leak", "Leaked credentials in dark web", "Investigating", "Critical", 50000L),
                createBreach("Ransomware Attack", "File server encrypted", "Contained", "High", 2000L),
                createBreach("Phishing Campaign", "Employee clicked malicious link", "Investigating", "Medium", 10L),
                createBreach("S3 Bucket Exposed", "Public S3 bucket exposed PII", "Resolved", "High", 150000L),
                createBreach("Lost Laptop", "Unencrypted laptop lost in transit", "Investigating", "Low", 500L),
                createBreach("API Token Leak", "GitHub repo exposed AWS keys", "Contained", "Critical", 0L),
                createBreach("Insider Threat", "Ex-employee downloaded CRM data", "Resolved", "High", 12000L),
                createBreach("DDoS Attack", "Website offline for 3 hours", "Resolved", "Medium", 0L),
                createBreach("Malware Infection", "Worm spreading in local network", "Contained", "Critical", 100L),
                createBreach("Misconfigured Firewall", "Unauthorised access to dev DB", "Investigating", "Low", 50L),
                createBreach("Third-Party Vendor Breach", "Supply chain attack via update", "Investigating", "Critical", 200000L),
                createBreach("Unauthorized Access", "Compromised admin account", "Contained", "High", 0L),
                createBreach("Data Exfiltration", "Large outbound data transfer detected", "Investigating", "Critical", 1000000L),
                createBreach("Physical Security", "Server room door left open", "Resolved", "Low", 0L),
                createBreach("SQL Injection", "Legacy web portal compromised", "Contained", "High", 8500L)
            );
            repository.saveAll(seedData);
        }
    }

    private DataBreach createBreach(String title, String description, String status, String severity, Long records) {
        DataBreach b = new DataBreach();
        b.setTitle(title);
        b.setDescription(description);
        b.setStatus(status);
        b.setSeverity(severity);
        b.setReportedDate(OffsetDateTime.now().minusDays((long) (Math.random() * 30)));
        b.setAffectedRecordsCount(records);
        return b;
    }
}
