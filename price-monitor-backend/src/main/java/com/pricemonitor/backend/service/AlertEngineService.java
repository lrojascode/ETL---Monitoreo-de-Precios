package com.pricemonitor.backend.service;

import com.pricemonitor.backend.model.PriceAlert;
import com.pricemonitor.backend.model.PriceHistory;
import com.pricemonitor.backend.model.Product;
import com.pricemonitor.backend.repository.PriceAlertRepository;
import com.pricemonitor.backend.repository.PriceHistoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class AlertEngineService {

    private final PriceHistoryRepository priceHistoryRepository;
    private final PriceAlertRepository priceAlertRepository;

    public void evaluatePriceAlert(Product product, PriceHistory currentPrice) {
        int currentEffectivePrice = currentPrice.getPricePromo() != null ? 
                                    currentPrice.getPricePromo() : currentPrice.getPriceNormal();

        // 1. Obtener precio promedio de los últimos 15 días móviles
        Instant limitDate = Instant.now().minus(15, ChronoUnit.DAYS);
        Double averagePrice = priceHistoryRepository.calculateAverageEffectivePriceForProduct(
                product.getId(), limitDate
        );

        if (averagePrice == null || averagePrice == 0.0) {
            return; // Sin histórico suficiente para calcular promedios
        }

        // 2. Calcular porcentaje de reducción
        double dropPercentage = ((averagePrice - currentEffectivePrice) / averagePrice) * 100;
        double threshold = 15.0; // Descuento crítico del 15%

        if (dropPercentage >= threshold) {
            log.info("ALERTA CRÍTICA: Detección de baja de precio para el producto '{}'. Precio actual: ${}, Precio promedio (15 días): ${} (Descuento del {}%)", 
                     product.getName(), currentEffectivePrice, Math.round(averagePrice), Math.round(dropPercentage));

            PriceAlert alert = new PriceAlert();
            alert.setProduct(product);
            alert.setPriceHistory(currentPrice);
            alert.setPercentageDrop(BigDecimal.valueOf(dropPercentage));
            alert.setIsResolved(false);
            priceAlertRepository.save(alert);
        }
    }
}
