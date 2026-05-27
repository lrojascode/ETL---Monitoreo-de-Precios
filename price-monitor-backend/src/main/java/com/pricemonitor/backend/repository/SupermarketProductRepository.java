package com.pricemonitor.backend.repository;

import com.pricemonitor.backend.model.SupermarketProduct;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SupermarketProductRepository extends JpaRepository<SupermarketProduct, UUID> {
    Optional<SupermarketProduct> findBySupermarketAndSkuSupermarket(String supermarket, String skuSupermarket);
}
