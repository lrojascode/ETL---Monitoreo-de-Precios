package com.pricemonitor.backend.repository;

import com.pricemonitor.backend.model.Brand;
import com.pricemonitor.backend.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ProductRepository extends JpaRepository<Product, UUID> {
    Optional<Product> findByNameIgnoreCaseAndBrand(String name, Brand brand);
}
