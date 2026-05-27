package com.pricemonitor.backend.repository;

import com.pricemonitor.backend.model.PriceHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.Instant;
import java.util.UUID;

@Repository
public interface PriceHistoryRepository extends JpaRepository<PriceHistory, UUID> {

    @Query(value = "SELECT AVG(LEAST(ph.price_normal, COALESCE(ph.price_promo, ph.price_normal))) " +
                   "FROM price_histories ph " +
                   "JOIN supermarket_products sp ON ph.supermarket_product_id = sp.id " +
                   "WHERE sp.product_id = :productId " +
                   "  AND ph.extraction_date >= :limitDate " +
                   "  AND ph.is_available = true", nativeQuery = true)
    Double calculateAverageEffectivePriceForProduct(
            @Param("productId") UUID productId,
            @Param("limitDate") Instant limitDate
    );
}
