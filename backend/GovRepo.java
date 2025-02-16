package com.UF.Urbanfix;

import org.springframework.data.jpa.repository.JpaRepository;
import com.smartcomplaint.model.Complaint;
import java.util.List;

public interface ComplaintRepository extends JpaRepository<Complaint, Long> {
    List<Complaint> findByStatus(String status);
    List<Complaint> findByAssignedDepartment(String department);
}