package com.pricemonitor.backend.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "price_alerts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PriceAlert {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "price_history_id", nullable = false)
    private PriceHistory priceHistory;

    @Column(name = "percentage_drop", nullable = false, precision = 5, scale = 2)
    private BigDecimal percentageDrop;

    @Column(name = "is_resolved")
    private Boolean isResolved = false;

    @Column(name = "created_at", updatable = false)
    private Instant createdAt = Instant.now();
}
