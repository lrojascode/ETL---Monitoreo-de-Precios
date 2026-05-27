package com.pricemonitor.backend.service;

import com.pricemonitor.backend.dto.IngestionPayload;
import com.pricemonitor.backend.dto.IngestionSummary;
import com.pricemonitor.backend.dto.ProductDto;
import com.pricemonitor.backend.model.*;
import com.pricemonitor.backend.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.Instant;

@Service
@RequiredArgsConstructor
public class IngestionService {

    private final BrandRepository brandRepository;
    private final CategoryRepository categoryRepository;
    private final ProductRepository productRepository;
    private final SupermarketProductRepository supermarketProductRepository;
    private final PriceHistoryRepository priceHistoryRepository;
    private final AlertEngineService alertEngineService;

    @Transactional
    public IngestionSummary processPayload(IngestionPayload payload) {
        int processedCount = 0;
        int newProductsCount = 0;

        Instant extractionTime = payload.getExtractionDate();
        String supermarket = payload.getSupermarket().toUpperCase();

        for (ProductDto dto : payload.getProducts()) {
            // 1. Obtener o crear Marca (Case-insensitive)
            String brandName = dto.getBrand().trim();
            Brand brand = brandRepository.findByNameIgnoreCase(brandName)
                    .orElseGet(() -> brandRepository.save(new Brand(brandName)));

            // 2. Obtener o crear Categoría (Case-insensitive)
            String categoryName = dto.getCategory().trim();
            Category category = categoryRepository.findByNameIgnoreCase(categoryName)
                    .orElseGet(() -> categoryRepository.save(new Category(categoryName)));

            // 3. Obtener o crear Producto de Catálogo Maestro por Nombre y Marca
            String productName = dto.getName().trim();
            Product product = productRepository.findByNameIgnoreCaseAndBrand(productName, brand)
                    .orElseGet(() -> {
                        Product p = new Product();
                        p.setName(productName);
                        p.setBrand(brand);
                        p.setCategory(category);
                        return productRepository.save(p);
                    });

            // 4. Obtener o crear mapeo SKU por Supermercado
            String sku = dto.getSkuSupermarket().trim();
            SupermarketProduct spProduct = supermarketProductRepository
                    .findBySupermarketAndSkuSupermarket(supermarket, sku)
                    .orElse(null);

            if (spProduct == null) {
                spProduct = new SupermarketProduct();
                spProduct.setProduct(product);
                spProduct.setSupermarket(supermarket);
                spProduct.setSkuSupermarket(sku);
                spProduct.setUrl(dto.getUrl().trim());
                spProduct = supermarketProductRepository.save(spProduct);
                newProductsCount++;
            } else {
                // Si ya existe, actualizamos url y estado por si cambiaron
                spProduct.setUrl(dto.getUrl().trim());
                spProduct.setIsActive(dto.getIsAvailable());
                spProduct = supermarketProductRepository.save(spProduct);
            }

            // 5. Registrar Historial de Precios
            PriceHistory priceHistory = new PriceHistory();
            priceHistory.setSupermarketProduct(spProduct);
            priceHistory.setPriceNormal(dto.getPriceNormal());
            priceHistory.setPricePromo(dto.getPricePromo());
            priceHistory.setExtractionDate(extractionTime);
            priceHistory.setIsAvailable(dto.getIsAvailable());
            PriceHistory savedPrice = priceHistoryRepository.save(priceHistory);

            // 6. Evaluar asíncronamente alerta de precio
            alertEngineService.evaluatePriceAlert(product, savedPrice);

            processedCount++;
        }

        return new IngestionSummary(processedCount, newProductsCount);
    }
}
