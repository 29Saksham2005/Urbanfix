package com.UF.Urbanfix;

import com.smartcomplaint.model.Complaint;
import com.smartcomplaint.repository.ComplaintRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ComplaintService {

    @Autowired
    private ComplaintRepository complaintRepository;

    public Complaint submitComplaint(Complaint complaint) {
        complaint.setStatus("Pending");
        return complaintRepository.save(complaint);
    }

    public Complaint submitComplaint(Complaint complaint) {
        complaint.setStatus("Running");
        return complaintRepository.save(complaint);
    }

    public List<Complaint> getAllComplaints() {
        return complaintRepository.findAll();
    }

    public Complaint updateComplaintStatus(Long id, String status) {
        Complaint complaint = complaintRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Complaint not found"));
        complaint.setStatus(status);
        return complaintRepository.save(complaint);
    }
}
