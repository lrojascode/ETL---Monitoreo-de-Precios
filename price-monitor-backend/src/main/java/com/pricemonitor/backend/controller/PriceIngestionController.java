package com.pricemonitor.backend.controller;

import com.pricemonitor.backend.dto.IngestionPayload;
import com.pricemonitor.backend.dto.IngestionResponse;
import com.pricemonitor.backend.dto.IngestionSummary;
import com.pricemonitor.backend.service.IngestionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/etl")
@RequiredArgsConstructor
public class PriceIngestionController {

    private final IngestionService ingestionService;

    @PostMapping("/ingest")
    public ResponseEntity<IngestionResponse> ingestPrices(@Valid @RequestBody IngestionPayload payload) {
        // La autenticación por X-API-KEY se maneja de manera centralizada en la capa de Spring Security
        IngestionSummary summary = ingestionService.processPayload(payload);
        
        IngestionResponse response = new IngestionResponse(
                "Ingesta procesada de forma exitosa", 
                summary
        );
        
        return ResponseEntity.ok(response);
    }
}
