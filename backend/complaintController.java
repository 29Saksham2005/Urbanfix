package com.UF.Urbanfix;

import com.smartcomplaint.model.Complaint;
import com.smartcomplaint.service.ComplaintService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/complaints")
public class ComplaintController {

    @Autowired
    private ComplaintService complaintService;

    @PostMapping("/submit")
    public ResponseEntity<Complaint> submitComplaint(@RequestBody Complaint complaint) {
        return ResponseEntity.ok(complaintService.submitComplaint(complaint));
    }

    @GetMapping("/all")
    public ResponseEntity<List<Complaint>> getAllComplaints() {
        return ResponseEntity.ok(complaintService.getAllComplaints());
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<Complaint> updateComplaintStatus(@PathVariable Long id, @RequestParam String status) {
        return ResponseEntity.ok(complaintService.updateComplaintStatus(id, status));
    }
}
