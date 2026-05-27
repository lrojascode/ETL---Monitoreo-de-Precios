package com.pricemonitor.backend.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "supermarket_products", uniqueConstraints = {
    @UniqueConstraint(columnNames = {"supermarket", "sku_supermarket"})
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class SupermarketProduct {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false, length = 50)
    private String supermarket;

    @Column(name = "sku_supermarket", nullable = false, length = 100)
    private String skuSupermarket;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String url;

    @Column(name = "is_active")
    private Boolean isActive = true;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at")
    private Instant updatedAt = Instant.now();

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = Instant.now();
    }
}
