package com.UF.Urbanfix;

import jakarta.persistence.*;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "complaints")
public class Complaint {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String description;
    private String compalintID;
    private String time;
    private String location;
    private String category;
    private String image;
    private String status = "Pending";
    private String status = "Running";
    private String assignedDepartment;

    @ManyToOne
    private User user;
}
