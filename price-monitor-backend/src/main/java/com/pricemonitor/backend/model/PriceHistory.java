package com.pricemonitor.backend.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "price_histories")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PriceHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "supermarket_product_id", nullable = false)
    private SupermarketProduct supermarketProduct;

    @Column(name = "price_normal", nullable = false)
    private Integer priceNormal;

    @Column(name = "price_promo")
    private Integer pricePromo;

    @Column(name = "extraction_date", nullable = false)
    private Instant extractionDate;

    @Column(name = "is_available")
    private Boolean isAvailable = true;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt = Instant.now();
}
