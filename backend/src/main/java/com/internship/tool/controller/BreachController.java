package com.internship.tool.controller;

import com.internship.tool.entity.DataBreach;
import com.internship.tool.service.DataBreachService;
import com.opencsv.CSVWriter;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/breaches")
@Tag(name = "Data Breach API", description = "Endpoints for managing data breaches")
public class BreachController {

    @Autowired
    private DataBreachService service;

    @Operation(summary = "Search data breaches", description = "Search across title and description")
    @GetMapping("/search")
    public ResponseEntity<List<DataBreach>> search(@RequestParam String q) {
        return ResponseEntity.ok(service.search(q));
    }

    @Operation(summary = "Update a data breach")
    @PutMapping("/{id}")
    public ResponseEntity<DataBreach> update(@PathVariable UUID id, @RequestBody DataBreach updatedBreach) {
        return service.findById(id).map(existing -> {
            existing.setTitle(updatedBreach.getTitle());
            existing.setDescription(updatedBreach.getDescription());
            existing.setStatus(updatedBreach.getStatus());
            existing.setSeverity(updatedBreach.getSeverity());
            return ResponseEntity.ok(service.save(existing));
        }).orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Soft delete a data breach")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Export data breaches to CSV")
    @GetMapping("/export")
    public void exportCSV(HttpServletResponse response) throws IOException {
        response.setContentType("text/csv");
        response.setHeader("Content-Disposition", "attachment; filename=\"breaches.csv\"");

        List<DataBreach> breaches = service.findAll();
        try (CSVWriter writer = new CSVWriter(response.getWriter())) {
            String[] header = {"ID", "Title", "Status", "Severity", "Reported Date"};
            writer.writeNext(header);

            for (DataBreach b : breaches) {
                String[] data = {
                        b.getId() != null ? b.getId().toString() : "",
                        b.getTitle(),
                        b.getStatus(),
                        b.getSeverity(),
                        b.getReportedDate() != null ? b.getReportedDate().toString() : ""
                };
                writer.writeNext(data);
            }
        }
    }

    @Operation(summary = "Upload file (e.g. proof of incident)")
    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body("File is empty");
        }
        if (file.getSize() > 5 * 1024 * 1024) { // 5MB limit
            return ResponseEntity.badRequest().body("File too large (max 5MB)");
        }
        String contentType = file.getContentType();
        if (contentType == null || (!contentType.equals("application/pdf") && !contentType.equals("image/png") && !contentType.equals("image/jpeg"))) {
            return ResponseEntity.badRequest().body("Invalid file type. Only PDF, PNG, JPG allowed.");
        }
        
        // In a real scenario, we would save the file
        return ResponseEntity.ok("File uploaded successfully: " + file.getOriginalFilename());
    }
}
